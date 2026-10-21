import json,sys
r=json.load(open(sys.argv[1]))["results"]; mode=sys.argv[2] if len(sys.argv)>2 else "strict"
cols=[("schemas_scanned","N"),("schemas_with_array_nodes_minitems_ge_1","minItems>=1"),("schemas_with_array_nodes_minitems_ge_2","minItems>=2"),("schemas_with_array_nodes_minitems_ge_1_no_maxitems","minItems>=1 & no maxItems"),("schemas_with_array_nodes_exact_length","min==max"),("schemas_with_required_properties_declared_array","required array prop"),("schemas_with_metadata_examples_concrete_looking","examples"),("schemas_with_metadata_example_concrete_looking","example (singular)"),("schemas_with_metadata_default_concrete_looking","default"),("schemas_with_metadata_description_eg_marker","desc e.g./for example"),("schemas_with_metadata_description_concrete_looking","desc concrete-looking (loose)")]
print("| subset | "+" | ".join(c[1] for c in cols)+" |"); print("|"+"---|"*(len(cols)+1))
for g,d in r.items():
    m=d[mode]; N=m.get("schemas_scanned",0)
    cells=[str(N)]+["%d (%.1f%%)"%(m.get(k,0),100*m.get(k,0)/N if N else 0) for k,_ in cols[1:]]
    print("| "+g+" | "+" | ".join(cells)+" |")
print()
print("| subset | array nodes | minItems>=1 nodes | min==max nodes | examples nodes | example nodes | default nodes |"); print("|---|---|---|---|---|---|---|")
for g,d in r.items():
    m=d[mode]; print("| %s | %d | %d | %d | %d | %d | %d |"%(g,m.get("array_nodes",0),m.get("array_nodes_minitems_ge_1",0),m.get("array_nodes_exact_length",0),m.get("metadata_examples_concrete_looking",0),m.get("metadata_example_concrete_looking",0),m.get("metadata_default_concrete_looking",0)))
