"""Tests for teacher_forced.py's pure parts (no model, no server). Run: python3 harness/tests/test_teacher_forced.py"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import teacher_forced as tf  # noqa: E402

F = "requests"


def test_layout_compact_closed():
    s = '{"requests":["Send the file","Call Bob"]}'
    lay = tf.list_layout(s, F)
    assert lay["stop"] == "closed"
    assert [s[a:b + 1] for a, b in lay["entries"]] == ['"Send the file"', '"Call Bob"']
    after, anchor, d, decision = zip(*lay["boundaries"])
    assert after == (-1, 0, 1) and decision == ("cont", "cont", "close")
    assert s[anchor[0]] == "[" and s[d[0]] == '"'
    assert s[d[1]] == "," and s[d[2]] == "]" and s[anchor[2]] == '"'
    assert tf.entry_texts(s, lay) == ["Send the file", "Call Bob"]


def test_layout_pretty_and_empty():
    s = '```json\n{\n  "requests": [\n    "a",\n    "b"\n  ]\n}\n```'
    lay = tf.list_layout(s, F)
    assert lay["stop"] == "closed" and tf.entry_texts(s, lay) == ["a", "b"]
    assert s[lay["boundaries"][-1][2]] == "]" and lay["boundaries"][-1][3] == "close"
    lay = tf.list_layout('{"requests": [ ]}', F)
    assert lay["stop"] == "closed" and lay["entries"] == [] and lay["boundaries"][0][3] == "close"


def test_layout_strings_with_brackets_and_escapes():
    s = '{"requests":["say \\"hi\\" ]}", "x, y"]}'
    lay = tf.list_layout(s, F)
    assert lay["stop"] == "closed" and tf.entry_texts(s, lay) == ['say "hi" ]}', "x, y"]


def test_layout_cut_off_keeps_complete_entries_only():
    s = '{"requests":["a","b","c'
    lay = tf.list_layout(s, F)
    assert lay["stop"] == "cut_off" and tf.entry_texts(s, lay) == ["a", "b"]
    lay = tf.list_layout('{"requests":["a","b"', F)            # ends right after an entry: not complete
    assert lay["stop"] == "cut_off" and tf.entry_texts('{"requests":["a","b"', lay) == ["a"]


def test_layout_odd_shapes():
    assert tf.list_layout('{"other":["a"]}', F)["stop"] == "no_list"
    assert tf.list_layout('{"requests":[1,2]}', F)["stop"] == "non_string_entry"
    assert tf.list_layout('{"requests":["a",]}', F)["stop"] == "trailing_comma"
    # a schema echo first, then the answer: the answer's list is the one found
    s = '{"requests": {"type": "array"}}\n{"requests":["a"]}'
    assert tf.entry_texts(s, tf.list_layout(s, F)) == ["a"]


def test_token_at_and_piece_offsets():
    starts, ends = [0, 2, 5], [2, 5, 7]
    assert [tf.token_at(starts, ends, d) for d in (0, 1, 2, 4, 5, 6)] == [0, 0, 1, 1, 2, 2]
    assert tf.token_at(starts, ends, 7) is None
    pieces = ["{", '"', "re", 'quests":["', "a", '","', "b", '"]}']
    ids = list(range(len(pieces)))
    s = "".join(pieces)
    spans = tf.piece_offsets(ids, pieces, s)
    assert spans[0] == (0, 1) and spans[-1] == (len(s) - 3, len(s))
    assert tf.piece_offsets(ids, pieces, s + "x") is None


def vocab():
    pieces = ['"', '",', '","', '"]', '"]}', '" ]', '"\n', ",", "]", "]}", " ]", "\n", " ", '":[', '":["',
              '":[]', '":[]}', "a", "b", '."', '.",', '."]}', ".", "<|end|>"]
    return pieces, tf.Vocab(pieces)


def test_candidates_by_residual():
    pieces, v = vocab()
    c = v.candidates('"', "entry")
    names = {k: sorted(pieces[i] for i in ids) for k, ids in c.items()}
    assert names["close"] == sorted(['"]', '"]}', '" ]'])
    assert names["cont"] == sorted(['",', '","'])
    assert names["open"] == sorted(['"', '"\n'])
    c = v.candidates("", "entry")
    names = {k: sorted(pieces[i] for i in ids) for k, ids in c.items()}
    assert names["close"] == sorted(["]", "]}", " ]"]) and names["cont"] == [","]
    assert names["open"] == sorted(["\n", " "])                    # whitespace only; never the empty piece
    c = v.candidates('":[', "start")
    names = {k: sorted(pieces[i] for i in ids) for k, ids in c.items()}
    assert names["close"] == sorted(['":[]', '":[]}']) and names["cont"] == ['":["'] and names["open"] == ['":[']
    c = v.candidates('."', "entry")
    assert sorted(pieces[i] for i in c["close"]) == ['."]}'] and [pieces[i] for i in c["cont"]] == ['.",']


def fake_pass(pieces, ids, lp_of):
    """prepare + finish with a stand-in model: lp_of(row, token id) -> log probability."""
    content = "".join(pieces[i] for i in ids)
    vocab = tf.Vocab(pieces)

    def encode(text):
        assert text == content
        return ids, tf.piece_offsets(ids, pieces, text), "pieces"
    lay = tf.list_layout(content, F)
    prep = tf.prepare(content, lay, [999, 998], encode, vocab)
    actual = [(lp_of(r, ids[r]), 1) for r in range(len(ids))]
    return prep, tf.finish(prep, actual, lambda row, vs: [lp_of(row, x) for x in vs])


def test_compact_boundaries_one_reading_each():
    pieces = ["{", '"', "requests", '":["', "a", '","', "b", '"]}']
    ids = list(range(len(pieces)))
    probs = {5: {5: 0.6, 3: 0.3}, 7: {7: 0.5}}                     # row -> {token id: probability}

    def lp_of(row, v):
        p = probs.get(row, {}).get(v, 1e-12)
        return math.log(p)
    pieces[3] = '":["'
    prep, res = fake_pass(pieces, ids, lp_of)
    b = res["boundaries"]
    assert [x["decision"] for x in b] == ["cont", "cont", "close"] and all(len(x["readings"]) == 1 for x in b)
    assert b[1]["readings"][0]["row"] == 5 and abs(b[1]["p_cont"] - 0.6) < 1e-6
    assert b[2]["readings"][0]["row"] == 7 and abs(b[2]["p_close"] - 0.5) < 1e-6
    assert b[1]["readings"][0]["actual_class"] == "cont" and b[2]["readings"][0]["actual_class"] == "close"
    assert res["align_max"] < 1e-9
    assert [e["n_tokens"] for e in res["entries"]] == [1, 1]


def test_pretty_print_two_readings_combine():
    # after "a": a bare quote token, then a newline, then "]": the first reading is at the newline's row
    pieces = ["{", '"', "requests", '":', " ", "[", "\n", '"', "a", '"', "\n", "]", "}"]
    ids = list(range(len(pieces)))
    # row 10 predicts "\n" (open), row 11 predicts "]" (close); "]" itself (id 11) at row 10 is a close too
    probs = {10: {10: 0.5, 11: 0.2, 4: 0.1}, 11: {11: 0.9}}

    def lp_of(row, v):
        return math.log(probs.get(row, {}).get(v, 1e-12))
    prep, res = fake_pass(pieces, ids, lp_of)
    last = res["boundaries"][-1]
    assert last["decision"] == "close" and len(last["readings"]) == 2
    first, second = last["readings"]
    assert first["row"] == 10 and abs(first["p_open"] - 0.6) < 1e-6 and abs(first["p_close"] - 0.2) < 1e-6
    assert second["row"] == 11 and abs(second["p_close"] - 0.9) < 1e-6
    assert abs(last["p_close"] - (0.2 + 0.6 * 0.9)) < 1e-6


def test_every_white_space_row_is_read():
    # '"a"' then "\n", then "  ", then "]": the "  " row is read too; half its mass starts a new entry
    pieces = ["{", '"', "requests", '":', " ", "[", "\n", '"', "a", '"', "\n", "  ", "]", "}"]
    ids = list(range(len(pieces)))
    probs = {10: {10: 1.0}, 11: {11: 0.5, 7: 0.5}, 12: {12: 1.0}}

    def lp_of(row, v):
        return math.log(probs.get(row, {}).get(v, 1e-12))
    prep, res = fake_pass(pieces, ids, lp_of)
    last = res["boundaries"][-1]
    assert [r["row"] for r in last["readings"]] == [10, 11, 12]
    assert abs(last["p_close"] - 0.5) < 1e-6


def test_later_rows_count_closes_with_less_white_space():
    # at the " ]" row, "]" (no space) closes the list as well
    pieces = ["{", '"', "requests", '":', " ", "[", "\n", '"', "a", '"', "\n", " ]", "}", "]"]
    ids = list(range(13))
    probs = {10: {10: 1.0}, 11: {11: 0.5, 13: 0.5}}

    def lp_of(row, v):
        return math.log(probs.get(row, {}).get(v, 1e-12))
    prep, res = fake_pass(pieces, ids, lp_of)
    assert abs(res["boundaries"][-1]["p_close"] - 1.0) < 1e-6


def test_too_many_ids_drops_go_on_sets_first():
    pieces = ["{", '"', "requests", '":["', "a", '","', "b", '"]}'] + [f'",{i}' for i in range(40)]
    ids = list(range(8))
    content = "".join(pieces[i] for i in ids)
    v = tf.Vocab(pieces)
    lay = tf.list_layout(content, F)
    enc = lambda text: (ids, tf.piece_offsets(ids, pieces, text), "pieces")  # noqa: E731
    full = tf.prepare(content, lay, [1], enc, v)
    small = tf.prepare(content, lay, [1], enc, v, max_ids=10)
    assert len(full["ids"]) > 10 >= len(small["ids"])
    assert all(r["classes"]["cont"] is None for b in small["bounds"] for r in b["readings"])


def test_exact_ids_drop_end_token_and_split_characters():
    class Tok:                                     # stand-in tokenizer: ids 2 and 3 are the two bytes of U+00E9
        text = {0: "J", 1: "os", 2: b"\xc3", 3: b"\xa9", 4: "<|end|>"}

        def decode(self, ids, **kw):
            out, raw = "", b""
            for i in ids:
                t = self.text[i]
                if isinstance(t, bytes):
                    raw += t
                    continue
                out += raw.decode("utf-8", "replace") + t
                raw = b""
            return out + raw.decode("utf-8", "replace")
    tok = Tok()
    pieces = ["J", "os", "\ufffd", "\ufffd", "<|end|>"]
    ids, spans, how = tf.exact_ids([0, 1, 2, 3, 4], "Jos\u00e9", tok, pieces)
    assert ids == [0, 1, 2, 3] and how == "generated_decoded"
    assert spans == [(0, 1), (1, 3), (3, 4), (3, 4)]
    ids, spans, how = tf.exact_ids([0, 1, 4], "Jos", tok, pieces)
    assert ids == [0, 1] and how == "generated" and spans == [(0, 1), (1, 3)]
    assert tf.exact_ids([0, 1], "Jo", tok, pieces) is None


def test_encoder_without_offset_mapping():
    class Tok:                                     # like MistralCommonBackend: no offset mapping
        text = {0: "J", 1: "os", 2: b"\xc3", 3: b"\xa9"}

        def __call__(self, text, **kw):
            raise ValueError("`MistralCommonBackend` does not support `return_offsets_mapping`")

        def encode(self, text, add_special_tokens=True):
            return {"Jos": [0, 1], "Jos\u00e9": [0, 1, 2, 3]}[text]

        def decode(self, ids, **kw):
            raw = b"".join(t if isinstance(t, bytes) else t.encode("utf-8") for t in (self.text[i] for i in ids))
            return raw.decode("utf-8", "replace")
    enc = tf.make_encoder(Tok(), ["J", "os", "\ufffd", "\ufffd"])
    assert enc("Jos") == ([0, 1], [(0, 1), (1, 3)], "pieces")
    assert enc("Jos\u00e9") == ([0, 1, 2, 3], [(0, 1), (1, 3), (3, 4), (3, 4)], "decoding")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    bad = 0
    for fn in fns:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            bad += 1
            print(f"FAIL {fn.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
