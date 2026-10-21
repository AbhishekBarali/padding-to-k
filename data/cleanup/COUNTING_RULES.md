# Counting rules for the answer lists

These are the rules the cleanup pass (13 Oct 2026) used to decide whether a document's answer list
(`gold_items`) and count (`n`) are right. They apply to every document of a set, not case by case.
Use the same rules when you check the data, so your checks and this pass can be compared.

The authors confirmed the rules on 13 Oct 2026, including the five calls that move the most documents:
M5 (the Project Manager's own jobs count), M4 (different jobs are separate items), V2 (a product is not
a feature of itself), E7 (advice in emails is borderline) and C4 (borderline medical substances).

## The one idea behind all of them

The study asks for k items from a document that has n. If k > n, every extra item a model returns
must be invented. That only holds if **n is the largest number of separate true items a careful reader
would list**. So:

- If the annotators missed a true item, n is too small and an honest model looks like it invents. Add it.
- If an annotator item is not really an item of that kind, n is too big. Remove it.
- If one annotator item holds two things a reader would list separately, split it.
- If two annotator items are really one thing, merge them.
- If a reasonable reader could get two different counts and no rule below settles it, the document has
  no single right answer. Drop it (or, in a set that is short of documents, leave it for the human check).

## Rules for every set

- **G1. Only the text counts.** An item is in the list only if the document itself shows it. Outside
  knowledge is used only to recognise what something is (that "lamivudine" is a drug).
- **G2. Never change the document.** Only the answer list changes. For quote and name sets, every item
  is copied exactly from the text (one unbroken stretch of it).
- **G3. One thing, one item.** The same thing mentioned twice, or under two forms ("DMSO" and
  "dimethyl sulfoxide", "Smith" and "John Smith" for one person), is one item.
- **G4. The to-do-list test for granularity.** Count the separate lines a careful person would write if
  they turned the document into a plain list of that kind. Two parts that could be done, bought or
  named on their own are two items. Parts that only describe one thing together are one item.
- **G5. Span edges are not errors.** Scoring is fuzzy, so an item whose span is a few words too long or
  short stays. A span is fixed only when it misses what the item is (cut mid-word, the wrong words, a
  broken fragment).
- **G6. Fix, drop or ask.** Fix when the right list is clear under these rules. Drop when the count
  depends on a borderline call, when the text is too garbled to tell, or when the count moves outside
  the study's range (below). Leave for the human check only a real judgment call in a set that cannot
  spare the document.
- **G7. Range.** Main study n = 0 to 3; the "asked for fewer than exist" arm n = 4 to 6 (meetings,
  emails, receipts, job_posts, clinical, reviews only). Receipts and reviews have no n = 0. A fix that
  moves a document outside its set's range drops it.

## Meetings (action items, AMI)

An action item is a job that a participant takes on, or is given, to do after this meeting.

- **M1. One item = one line of the to-do list** written after the meeting: one job with its owner(s).
- **M2. A job done together** by several people is one item ("you two build the prototype together").
- **M3. The same job given to several people** is one item ("everyone fill in the questionnaire").
- **M4. Different jobs are separate items**, even for the same person or in one annotator sentence.
  "The Marketing Expert will find out the display cost and present his marketing strategy" is two items.
- **M5. The Project Manager's own jobs count** when said as a commitment ("I'll put the minutes in the
  project folder", "I will submit it to management").
- **M6. Not action items:** decisions about the product ("we'll go with rubber buttons"); things done in
  the meeting itself ("I'll draw it on the board"); vague intentions with no job ("we should keep costs
  in mind"); ideas raised and then dropped or postponed with no owner ("let's skip it for now");
  scheduling remarks ("next meeting is in thirty minutes", "you'll get instructions by email").
- **M7. Wording.** A split or added item is one plain sentence in the annotators' style ("The Industrial
  Designer will look into the cost of the display.") with the transcript lines it rests on as evidence.
- **M8. "Everyone goes back to their individual work"** (the AMI break between meetings) is one item only
  when the window gives no specific job to anyone; next to the specific role jobs it adds nothing. "You will
  get instructions from your coach / by email" is never a job (M6).
- **M9. The final questionnaire and the meeting summary** are two jobs (the annotators split them too).

## Emails (requests, MailEx)

A request is something the sender asks the reader to do, give, answer or decide.

- **E1. Counts:** commands ("Please send the report"); questions that ask the reader for information or a
  decision ("What is the total cost?", "Would you like me to extend it for 3 or 6 months?"); polite
  requests ("Could you...", "I would appreciate it if you...", "Any help you can provide would be
  appreciated").
- **E2. Does not count:** statements of fact, plans or needs that ask nothing of the reader ("we are
  required to put an end date in our system"); the sender's own promises ("I'll call you tomorrow");
  thanks; pointers ("see attached", "please note that...", "FYI"); conditional offers and sign-offs
  ("let me know if you have any questions", "call me if you need anything", "feel free to call").
- **E3. "We need to..."** is a request only when it is plainly the reader's job and no explicit request in
  the email already covers it.
- **E4. One item per thing asked.** A question asked again in other words, or with alternatives
  ("Which contracts do you mean, A or B? Or something else?") is one item. Two different things asked
  are two items, even in one sentence.
- **E5. Subject line** is part of the email. A request that appears only in the subject counts; one that
  the body repeats is the same item. An inherited "RE:"/"FW:" subject does not count on its own.
- **E6. Someone else's message.** If the shown text contains a forwarded or quoted message whose
  requests were made by another person, the count is unclear: drop.
- **E7. Advice is borderline.** "I would recommend that...", "it would be a good idea to...", and a third
  person's suggestion passed on ("Jeff has suggested that legal could...") may or may not be requests: if
  the count depends on one, drop. "Let's meet" / "I'd like to discuss" with the reader counts (E1).
- **E8. "Do X and let me know what you think"** is two items (the reply is a separate act). "Let me know"
  or "please advise" that only repeats a question already asked is the same item (E4).

## Receipts (items purchased, CORD)

- **R1. One item per product bought**, named as printed (a name wrapped over two lines is one item).
- **R2. Not items:** totals, subtotals, tax, service charge, discounts, payment, change, item counts.
- **R3. Modifiers and set contents** (toppings, "less sugar", the parts of a set menu) belong to their
  parent item. If such a line has its own non-zero price, it reads as a separate purchase: drop.
- **R4. Free items** (price 0) still count. The same product printed twice is one item (G3).
- **R5.** If you cannot tell which lines are products (garbled OCR), drop.
- **R6. Price-0 lines** are free items (R4) when they stand alone (a bag, a container, a free drink). When
  they read as the contents of a priced set (fries and sauce under a combo), R3 and R4 disagree: drop.

## Clinical (medications, MACCROBAT)

- **C1. Counts:** a drug, by name or by class, that the patient was given or was taking ("lamivudine",
  "antibiotics", "steroids"). Earlier medication history counts.
- **C2. Does not count:** procedures and therapies that are not a substance (surgery, radiotherapy,
  dialysis, "chemoembolization"); tests; devices; drugs that were not given (negated, planned and not
  given, considered, allergies); another person's drugs.
- **C3. A class word for the same treatment as a named drug** is one item ("chemotherapy with cisplatin"
  is cisplatin). A class with no named drug is its own item.
- **C4. Borderline substances** (oxygen, saline and other fluids, blood products, nutrition, contrast
  agents, solvents, embolic agents, anaesthesia named only as "general anesthesia" or "sedation", drugs of
  abuse) decide nothing: if the count depends on one, drop.
- **C5. Combination drugs.** One item when the partner is not a drug on its own (piperacillin/tazobactam);
  two when each part is a drug on its own (emtricitabine + tenofovir).

## Job ads: skills (SkillSpan)

- **J1. Counts:** an ability, soft skill, personal quality or duty the employee is expected to have or do
  ("work independently", "strong communicator", "manage projects"). Duties count: that is SkillSpan's
  definition and what the prompt asks for.
- **J2. Does not count:** tools, technologies, fields, languages, degrees and certificates (those are the
  knowledge list); years of experience; text about the company, benefits or how to apply; job titles.
- **J3. Lists.** "Extrovert and a strong communicator" is two items; "analytical and problem-solving
  skills" is two. One verb with one object stays one item ("plan and run the weekly sales meeting").
- **J4. Lost commas.** The source removed most commas. If a run of words cannot be split into items with
  one clear reading, drop.

## Job ads: knowledge (SkillSpan)

- **K1. Counts:** tools, software, programming languages, technologies, methods with a name, fields of
  knowledge or study ("computer science", "gynaecology"), spoken languages, certificates and licences.
- **K2. Does not count:** abilities and duties (skills list), the company's own products or industry when
  they only describe the company, job titles, anonymised placeholders on their own (`<ORGANIZATION>`).
- **K3. Lists** are split as in J3; lost commas as in J4.
- **K4. A degree** ("a Master's degree") is not an item on its own; its field is ("in finance").
- **K5. Slash pairs** ("WordPress/PHP", "Scrum/Agile") are two items (K3).

## Wikipedia sentences: people (Few-NERD)

- **W1. Counts:** a named individual person, real or legendary, mentioned in the sentence.
- **W2. Does not count:** groups, bands, families, duos, teams; a name used inside the name of something
  else (a prize, building, company, book or comic series: "the Asterix comic book series", "Nobel
  Prize"); pronouns; titles without a name ("the president").
- **W3. Fictional characters and gods** are borderline: if the count depends on one, drop. Names in a
  sentence that retells a film's or a show's plot are characters.
- **W4. One person, one item** (G3), even when written two ways.

## Novels: direct speech (PDNC)

- **Q1. One item per quotation:** the words between an opening and a closing quote mark. A quoted thought
  ("...," thought Alice) counts: it is in quote marks, and a model that lists it is not inventing.
- **Q2. A quotation interrupted by a speech tag** ("A," she said, "B.") can be counted as one item or two,
  so a document that has one is dropped (the set has spares). The same goes for one speaker continuing
  after a paragraph break.
- **Q3. Two identical quotations** ("No." said twice) are a borderline count: drop.
- **Q4. Not items:** reported speech without quote marks, thoughts without quote marks, titles in quotes.

## Reviews: features (ROAST)

- **V1. Counts:** a feature or aspect of the product or service (a part, a property or a service element:
  staff, location, price, battery, autograder, taste) that the reviewer gives an opinion on, named by a
  word or phrase in the text.
- **V2. The product or service as a whole is not a feature of itself** ("the hotel", "this course", the
  product's brand name). It comes out of the list.
- **V3. Mentioned without an opinion** is not an item ("we stayed two nights").
- **V4.** If the reviewer clearly judges an aspect that the text never names in a word (and a reader
  would list it), the count is unclear: drop.
- **V5. Borderline targets:** the shop, platform or seller (Amazon, Coursera, a university), other products
  or flavours of the brand, and a thank-you with no opinion. If the count depends on one, drop.
- **V6. A property of a feature folds into it** (the instructor's clarity is the instructor; the room's
  cleanliness is the room, when the room is named).
- Review text is never written into the repo. Changes to reviews are stored as character positions.
