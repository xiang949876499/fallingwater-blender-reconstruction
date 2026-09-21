# Full09 independent graph and integer-frame audit

Source SHA: `489b05e403aa9d02c3568a8e3813a24235ee5b7e782df4d1f149b3ff6673e331`. Actual saved room cameras were read before any tour animation was built; production camera settings were not applied.

60-edge graph: **{'PASS': 58, 'FAIL': 2, 'NOT_RUN': 0}**. Normal walking PASS 50; inspection-only PASS 8. These categories remain distinct.

Delivered integer-frame audit: 7584 frames; 0 mesh failures; coverage `PASS_CAMERA_VALUES_AND_COVERAGE`. This does not convert the connection graph to PASS.

No checked09 scene was saved. Candidate route evidence is under the09-prefixed QA files; production `data/tour-route.json` was not overwritten. Overall: `FAIL_FULL_CONNECTION_GRAPH_NO_CHECKED_SCENE_SAVED`.
