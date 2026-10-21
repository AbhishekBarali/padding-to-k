# Possible shortfall notes in the dev-set outputs

Runs: 2026-10-14_qwen3.5-9b_dev, 2026-10-14_ministral-3-14b_dev, 2026-10-14_gemma-4-31b_dev. Entries parsed: 17059 (review set left out: it stays local).
Listed: entries of at most 4 words, or with no / none / not / only / other / additional / found; same text after normalising counted together.

Left out: 1191 distinct entries copied word for word from their document (8185 times), since the rules never treat copied text as a note.

## Not in the document, counted as items by the current rules: 518 distinct entries

Read these. Any that is a note about a shortfall rather than an item of the asked kind should be added to the placeholder rules (harness/common.py) before the freeze. "rules say note" counts the times the rules already treat it as a note (an entry copied from the document never is).

### With no / none / not / only / other / additional / found: 201 (read these first)

| entry | times | rules say note | copied from the document | conditions | sets | models |
|---|---|---|---|---|---|---|
| None mentioned in the provided document. | 22 | 0 | 0 | min_k_enforced 22 | clinical 22 | ministral-3-14b |
| provide information to complete the attached schedule regarding AR, AP, and shipped but not billed amounts ... | 8 | 0 | 0 | min_k_enforced 3, min_k_shown 2, max_k_shown 2, none 1 | emails 8 | ministral-3-14b, qwen3.5-9b |
| submit your bid no later than December 12, 2001 @ 10:00 a.m. EST | 8 | 0 | 0 | max_k_shown 2, min_k_enforced 2, min_k_shown 2, none 2 | emails 8 | ministral-3-14b, qwen3.5-9b |
| no | 5 | 0 | 0 | min_k_enforced 5 | clinical 5 | qwen3.5-9b |
| provide information on whether or not the Enron commitment will be honored as was communicated in the e-mail | 5 | 0 | 0 | none 2, min_k_enforced 2, max_k_shown 1 | emails 5 | ministral-3-14b, qwen3.5-9b |
| Confirm if John and Jim are happy for Clifford Chance to act commercially on the other side of the table fr... | 4 | 0 | 0 | max_k_shown 2, min_k_shown 2 | emails 4 | qwen3.5-9b |
| Ed will find out the additional cost of adding a display. | 4 | 0 | 0 | max_k_shown 2, none 1, min_k_enforced 1 | meetings 4 | gemma-4-31b |
| Provide copies of any other documents related to the December 13, 1999 prepay, or confirm if there are no o... | 4 | 0 | 0 | max_k_shown 2, none 1, min_k_shown 1 | emails 4 | qwen3.5-9b |
| Provide information about any numbers you are not comfortable with as I am compiling a detailed schedule of... | 4 | 0 | 0 | max_k_shown 2, min_k_shown 1, none 1 | emails 4 | ministral-3-14b |
| provide me with information to complete the attached schedule regarding AR, AP, and shipped but not billed ... | 4 | 0 | 0 | max_k_shown 2, min_k_shown 1, none 1 | emails 4 | qwen3.5-9b |
| forward the e-mail if you know of someone who should receive it but who has not | 3 | 0 | 0 | max_k_shown 1, none 1, min_k_shown 1 | emails 3 | qwen3.5-9b |
| get additional data including addresses and phone numbers | 3 | 0 | 0 | min_k_enforced 2, min_k_shown 1 | emails 3 | ministral-3-14b, qwen3.5-9b |
| let me know if you want to stay over even though it's not at the end of the week | 3 | 0 | 0 | min_k_shown 2, max_k_shown 1 | emails 3 | qwen3.5-9b |
| Please review the attached draft of Transwestern's response to the protest filed by the California Public U... | 3 | 0 | 0 | max_k_shown 2, none 1 | emails 3 | qwen3.5-9b |
| Proceed with the changes to TW's tariff (assuming no meeting is needed) | 3 | 0 | 0 | max_k_shown 2, none 1 | emails 3 | ministral-3-14b |
| Provide information about any numbers you are not comfortable with as part of a detailed schedule of except... | 3 | 0 | 0 | min_k_enforced 2, min_k_shown 1 | emails 3 | ministral-3-14b |
| Provide information as of 11/30/01 for the following point people: Leslie Reeves (ENA: AR, AP, Shipped but ... | 3 | 0 | 0 | max_k_shown 2, none 1 | emails 3 | ministral-3-14b |
| Send the rest of the San Juan and West of Thoreau contracts if the recipient does not already have them. | 3 | 0 | 0 | max_k_shown 2, none 1 | emails 3 | qwen3.5-9b |
| The user interface team will notify the other participants when the modeling is complete. | 3 | 0 | 0 | max_k_shown 2, none 1 | meetings 3 | qwen3.5-9b |
| Clarify if the environmental disclosures are a separate document needed for the data room if the footnotes ... | 2 | 0 | 0 | min_k_shown 2 | emails 2 | qwen3.5-9b |
| Determine if Bridgeline Gas Distribution should be removed from the approved bidders list due to no activit... | 2 | 0 | 0 | max_k_shown 2 | emails 2 | qwen3.5-9b |
| Ensure buttons are large enough to be easily found and pressed. | 2 | 0 | 0 | max_k_shown 1, min_k_shown 1 | meetings 2 | qwen3.5-9b |
| Ensure Ray attends the AAI Meeting (as he is local and no cost is involved) | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | emails 2 | ministral-3-14b |
| Ensure your bid is submitted no later than December 12, 2001 @ 10:00 a.m. EST | 2 | 0 | 0 | max_k_shown 2 | emails 2 | ministral-3-14b |
| If Bridgeline Gas Distribution is not removed from the approved bidders list, ensure it is listed on the gu... | 2 | 0 | 0 | min_k_shown 1, none 1 | emails 2 | ministral-3-14b, qwen3.5-9b |
| If Bridgeline Gas Distribution is not removed from the approved bidders list, include it on the guaranty. | 2 | 0 | 0 | none 1, min_k_shown 1 | emails 2 | qwen3.5-9b |
| If Bridgeline Gas Distribution is not removed, ensure it is listed on the guaranty. | 2 | 0 | 0 | max_k_shown 1, min_k_shown 1 | emails 2 | ministral-3-14b |
| If Bridgeline Gas Distribution is not removed, list it on the guaranty as well. | 2 | 0 | 0 | max_k_shown 2 | emails 2 | qwen3.5-9b |
| Locate documents in connection with a prepay (December 13, 1999) among ENA, Citibank, Barclays, Royal Bank ... | 2 | 0 | 0 | min_k_shown 1, max_k_shown 1 | emails 2 | ministral-3-14b |
| not | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | qwen3.5-9b |
| Note that only the first 4 of 8 pages are planned for inclusion. | 2 | 0 | 0 | min_k_enforced 2 | emails 2 | qwen3.5-9b |
| Provide copies of the ISDA, swap confirms, or any other documents related to the December 13, 1999 prepay | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | emails 2 | ministral-3-14b |
| Reconsider the voice recognition feature as it is not selected. | 2 | 0 | 0 | max_k_shown 2 | meetings 2 | qwen3.5-9b |
| Research and evaluate the feasibility of dynamically lighting only applicable buttons to reduce battery usage | 2 | 0 | 0 | max_k_shown 2 | meetings 2 | ministral-3-14b |
| The user interface team will inform the other participants if they can finish earlier than expected. | 2 | 0 | 0 | none 1, max_k_shown 1 | meetings 2 | qwen3.5-9b |
| Track down an answer for whether or not the Enron commitment will be honored as was communicated in the e-mail | 2 | 0 | 0 | min_k_shown 2 | emails 2 | ministral-3-14b |
| ). Since the schema requires at least **3 medication entries**, and the document only mentions | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| 6-MP (6-mercaptopurine)]}```json is not valid here since the document does not explicitly list medications ... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| ]. However, since the document does not contain a third quotation, I cannot fulfill the `minItems: 3` const... | 1 | 0 | 0 | min_k_enforced 1 | novel_quotes 1 | qwen3.5-9b |
| ]} ``` For a valid instance, additional medications would need to be included. Would you like me to adjust ... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| ]} ``` If you need a valid JSON output, please provide additional information or clarify the requirements. ... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| ]} ```. However, this is **invalid** because it does not meet the `minItems: 5` requirement. The document d... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| Acknowledge the collective sentiment that the deal has not met expectations | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| All team members to confirm their availability for the next meeting and any additional tasks they can contr... | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| anti-VEGF therapy (e.g., ranibizumab, aflibercept, or bevacizumab) or other intravitreal injections (e.g., ... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antibiotics (unspecified) (given unsuccessfully)]}The provided document does not explicitly list a comprehe... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antibiotics (unspecified) (used unsuccessfully)]}The provided document does not explicitly list a comprehen... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antidiabetic medications (general category, as specifics are not mentioned)]}** | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antiretroviral therapy (ART) (specific regimen not mentioned) (since May 2010) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Assess the durability and sensitivity of the clapping device to ensure it is not easily breakable or overly... | 1 | 0 | 0 | max_k_shown 1 | meetings 1 | ministral-3-14b |
| Assess the need for additional special button supplements and update the cost estimate accordingly. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| assess whether you are the only person who can understand and evaluate the opportunity | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Calculate the additional selling price for the display option. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | qwen3.5-9b |
| call with any questions, comments, concerns (713 853 9123) please provide information for ENA: Leslie Reeve... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Can you please confirm if the new keep whole GTCs are primary term, given there is no mention in either the... | 1 | 0 | 0 | none 1 | emails 1 | qwen3.5-9b |
| Clarify and document the durability requirements for the clapping device to ensure it is not overly sensiti... | 1 | 0 | 0 | none 1 | meetings 1 | ministral-3-14b |
| Clarify any additional details or updates needed for the forecasts | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Clarify if a separate document is needed for the 'data room' if the footnotes are not the correct disclosures. | 1 | 0 | 0 | none 1 | emails 1 | qwen3.5-9b |
| Clarify if a separate document is needed for the data room if the footnotes are not the correct disclosures. | 1 | 0 | 0 | max_k_shown 1 | emails 1 | qwen3.5-9b |
| Clarify if a separate document is needed for the data room if the footnotes are not the requested disclosures. | 1 | 0 | 0 | max_k_shown 1 | emails 1 | qwen3.5-9b |
| Compile the responses into one form (along with Leonard Daily and any other participants) and submit it | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Confirm if there is an additional document required for the 'data room' beyond the audited financials. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Confirm the button count and functionality to ensure it aligns with user needs and remains minimal (only ne... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Design a new remote control that is lightweight and not too heavy. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| Design a remote control with a weight that is not too heavy. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | qwen3.5-9b |
| Determine if additional special button supplements are needed and their impact on cost/time. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| Determine if Bridgeline Gas Distribution should be removed from the approved bidders list given no activity... | 1 | 0 | 0 | none 1 | emails 1 | qwen3.5-9b |
| Determine if Bridgeline Gas Distribution should be removed from the approved bidders list given no activity... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | qwen3.5-9b |
| Determine whether Bridgeline Gas Distribution should be removed from the approved bidders list given no act... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | qwen3.5-9b |
| Develop a minimalist remote control design with only channel, volume, power, and audio buttons as the prima... | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| do I need to apply online? (implied as a request for clarification)]}Here is the JSON instance conforming t... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Do I need to apply online? (implied request for clarification on application process)]}Here is the JSON ins... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| do you think there is any continuing interest in your shop for the contract audit matter we discussed? (imp... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Document contains only 1 item, but schema requires at least 5. | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| Document does not reference medications. | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Document the agreed-upon scoring system (e.g., 1 = very fancy, 7 = not fancy at all) for reference in futur... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Ed will find out the additional cost of adding a display to the device. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | gemma-4-31b |
| Ensure Tasking Letter is not processed until GSA is executed | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Ensure the buttons are large enough to be easily found and pressed. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | qwen3.5-9b |
| Ensure the response supports the statement that USGT has not made significant use of its westward capacity. | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Evaluate and finalize the button count to ensure only necessary buttons are included. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| Evaluate and finalize the button design to ensure it meets the 'necessary buttons only' criterion and test ... | 1 | 0 | 0 | max_k_shown 1 | meetings 1 | ministral-3-14b |
| everolimus (10 mg daily)]} is not valid because it does not meet the `minItems: 3` requirement. Since the p... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| everolimus (10 mg daily)]} is not valid because it does not meet the `minItems: 5` requirement in the schem... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Exclude the last 4 pages from the presentation (they were built anticipating Andersen being involved and ar... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Explain the distinction between the footnotes in the audited financials and any additional environmental di... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Explore and evaluate additional technology features (e.g., speech recognition, location-based, and LCD colo... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Finalize the button count and ensure it aligns with the 'necessary buttons only' criterion (rating: 1). | 1 | 0 | 0 | none 1 | meetings 1 | ministral-3-14b |
| Finalize the cost breakdown for the 12 buttons (€12 each) and the scroll wheel, including any additional su... | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| Finalize the rating scale definition where 1 represents 'very fancy' and 7 represents 'not at all fancy'. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| Finalize the voting scale definition where 1 represents 'very fancy' and 7 represents 'not fancy at all'. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| Follow up with the Industrial Designer to confirm their willingness to adjust their score (5) or provide ad... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| for compliance, though this is not semantically accurate): ```json { | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| forward this e-mail if you know of someone who should receive it but who has not | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| forward this email to anyone who should receive it but has not | 1 | 0 | 0 | none 1 | emails 1 | ministral-3-14b |
| get additional data including addresses and phone numbers when an individual is selected | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Identify any additional attendees who should be included in the meetings | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Identify names of additional attendees for the meetings | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| if Bridgeline Gas Distribution is not taken off the approve bidders list, list it on the guaranty as well | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| If Bridgeline Gas Distribution is not to be removed, ensure it is listed on the guaranty as well. | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| in a vague context, I cannot fulfill the schema's `minItems: 3` requirement with the given information alon... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Incorporate a battery indicator (e.g., LED) to ensure users can easily check battery status without additio... | 1 | 0 | 0 | none 1 | meetings 1 | ministral-3-14b |
| Incorporate the additional information into the draft response if necessary. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Investigate technical feasibility of dynamically lighting only applicable buttons to reduce battery usage | 1 | 0 | 0 | none 1 | meetings 1 | ministral-3-14b |
| List the names of any additional attendees for the meetings. | 1 | 0 | 0 | max_k_shown 1 | emails 1 | qwen3.5-9b |
| Make the buttons large enough to be easily found and pressed. | 1 | 0 | 0 | none 1 | meetings 1 | qwen3.5-9b |
| No follow-up actions are required based on the given text. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| No instructions or tasks are outlined for the recipient. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| No prescription drugs noted. | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| None applicable | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| none documented | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| none mentioned in the provided document (no medications listed) or implied by the clinical context. | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| none mentioned in the provided document (no medications listed)]}The provided document does not mention any... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| none mentioned in the provided document (patient history does not list medications)]}The provided document ... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| note the sender's decision not to share RAC updated valuation numbers with ECR | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| note the sender's statement that ECR should no longer be privy to that type of ENE info | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Please confirm if there are any other actions or clarifications needed from your side. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Please confirm if there are any other requests or clarifications needed. | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Please confirm if there is no mention in either the Confirm or the GTC language regarding the new keep whol... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Please confirm if there is no mention of the new keep whole GTCs being primary term in either the Confirm o... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Please ensure the Tasking Letter is not processed until GSA is executed and language has been agreed upon. | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Please note we are only planning on including the first 4 of 8 pages | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| Please provide at least five requests as per the schema requirements, but the provided document contains no... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| please provide information for EEL metals NY/US companies: Louis Colarusso, Claire Wright prm net asset, li... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| please provide information for EEL, gas, power: David Oliver: prm net asset, liabilities, AR, AP, shipped b... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| please provide information for EGM ECTRIC: Cindy Horn/Melissa Allen: prm net asset, liabilities, AR, AP, sh... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| please provide information for EGM, EIM: Kevin Sweeney: AR, AP, Shipped but not billed, Angeles Beltri: rec... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| please provide information for EIM ECTRIC: Jenny Latham: split out of ECTRIC from receivership, AR, AP, shi... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| please provide information for NORDIC ECTRIC: Matthew Landy: prm net asset, liabilities, AR, AP, shipped bu... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Please review the additional information from Mark on USGT's use of westward capacity. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Please review the additional information from Mark on USGT's use of westward capacity and provide feedback ... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Please use the last 4 pages for reference only | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| Popcorn Salt (S) {Note: The document provided contains only 2 items, but the schema requires a minimum of 5... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | gemma-4-31b |
| Popcorn Salt (S) {Note: The schema requires minItems 3, but only 2 items are present in the text. Including... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | gemma-4-31b |
| Popcorn Salt (S)']}**Note: The document only contains 2 items, but the schema requires at least 3 (`minItem... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | qwen3.5-9b |
| Popcorn Salt (S)]} is not valid because it does not meet the `minItems: 3` requirement in the schema. Since... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| Popcorn Salt (S)]} is not valid because it does not meet the `minItems: 5` requirement in the schema. Since... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| Project Manager will review the feasibility of lighting only applicable buttons to reduce battery usage. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| provide additional information from Mark on USGT's use of westward capacity | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| provide any information on whether or not the Enron commitment will be honored as was communicated in the e... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Provide copies of any other documents related to the December 13, 1999 prepay, or confirm if there are no o... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | qwen3.5-9b |
| Provide feedback on whether the names are fun or not | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide feedback on whether the names are funny or not | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information as of 11/30/01 for the following point people: Leslie Reeves (ENA: AR, AP, Shipped but ... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information as of 11/30/01 for the following point people: Leslie Reeves (ENA: AR, AP, Shipped but ... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for EEL metals NY/US companies: Louis Colarusso and Claire Wright for prm net asset, li... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for EEL metals NY/US companies: Louis Colarusso and Claire Wright regarding prm net ass... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for EEL, gas, power: David Oliver for prm net asset, liabilities, AR, AP, shipped but n... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for EEL, gas, power: David Oliver regarding prm net asset, liabilities, AR, AP, shipped... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for EGM ECTRIC: Cindy Horn/Melissa Allen for prm net asset, liabilities, AR, AP, shippe... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for EGM ECTRIC: Cindy Horn/Melissa Allen regarding prm net asset, liabilities, AR, AP, ... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for EGM, EIM: Kevin Sweeney for AR, AP, Shipped but not billed, and Angeles Beltri for ... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for EGM, EIM: Kevin Sweeney regarding AR, AP, shipped but not billed, and Angeles Beltr... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for EIM ECTRIC: Jenny Latham for split out of ECTRIC from receivership, AR, AP, shipped... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for EIM ECTRIC: Jenny Latham regarding split out of ECTRIC from receivership, AR, AP, s... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for ENA: Leslie Reeves for AR, AP, and Shipped but not billed. | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for ENA: Leslie Reeves regarding AR, AP, and shipped but not billed. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Provide information for NORDIC ECTRIC: Matthew Landy for prm net asset, liabilities, AR, AP, shipped but no... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Provide information for NORDIC ECTRIC: Matthew Landy regarding prm net asset, liabilities, AR, AP, shipped ... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Reach out to the User Interface team to finalize their rating (4) and gather additional feedback on the rem... | 1 | 0 | 0 | none 1 | meetings 1 | ministral-3-14b |
| Red dragon (P) {Note: The document provided contains only 3 items, but the schema requires a minimum of 5. ... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | gemma-4-31b |
| Red dragon (P)]} is not valid because it does not meet the `minItems: 5` requirement in the schema. However... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| Research and compile a list of additional technology features (e.g., speech recognition, location-based, LC... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Research and document the battery consumption impact of selectively lighting only applicable buttons in the... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Research and document the battery usage impact of selectively lighting only applicable buttons in the devic... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Revisit the cost analysis to ensure the product remains under budget while meeting all other criteria. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| Schedule a follow-up discussion if additional details or decisions are needed before diving deeper into the... | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| Schedule a follow-up meeting to finalize the remote control design changes (Mando Banana vs. existing TV re... | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| Send the revised policy to other Infrastructure Sr. Directors/Directors for review | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Share additional details about the role, | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Share any additional requirements for the audit process. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| sildenafil (20 mg twice per day)]} is not valid because it does not meet the `minItems: 5` requirement in t... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| sildenafil (20 mg twice per day)]}**⚠️ Note:** The provided example only contains **2 medications**, but th... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| simple analgesia (e.g., paracetamol/ibuprofen)]}The provided document mentions only **two medications** (`c... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| steroid injections (if applicable, though not explicitly mentioned) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Sure then I'm here! Digging for apples, yer honour!']}**Note: The document contains only two direct quotati... | 1 | 0 | 0 | min_k_enforced 1 | novel_quotes 1 | qwen3.5-9b |
| Sure then I'm here! Digging for apples, yer honour!']}**Note: The extracted quotations are direct speech fr... | 1 | 0 | 0 | min_k_enforced 1 | novel_quotes 1 | qwen3.5-9b |
| tazobactam/piperacillin (TAZ/PIPC) (4.5g q12h)]} is not valid because it does not meet the `minItems: 3` re... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| tazobactam/piperacillin (TAZ/PIPC) (4.5g q12h)]} is not valid because it does not meet the `minItems: 5` re... | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Team to acknowledge that changing the remote control to a 'Mando banana' is not feasible. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | qwen3.5-9b |
| THAI ICED TEA (L)]} is not valid because it does not meet the `minItems: 5` requirement in the schema. Sinc... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| The document consists only of narrative description. | 1 | 0 | 0 | min_k_enforced 1 | novel_quotes 1 | gemma-4-31b |
| The Industrial Designer will finalize the basic, minimalist design (audio button only) as a selling point. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | ministral-3-14b |
| The last 4 pages were built anticipating Andersen being involved and are included for reference only. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| The Project Manager will provide additional details via the personal coach regarding next steps and respons... | 1 | 0 | 0 | none 1 | meetings 1 | ministral-3-14b |
| The User Interface Designer will explore a minimalist audio-button-only design for the remote control. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | ministral-3-14b |
| The user interface team will inform the other participants if the modeling can be completed earlier than ex... | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| The user interface team will notify the other participants if the modeling is finished earlier than expected. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| The user interface team will notify the other participants when the modeling is finished. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| There is no mention in either the Confirm or the GTC language regarding the primary term of the new keep wh... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| to confirm if there are no objections from the Enron Europe Legal Department | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| topical steroid (not mentioned but often used for rashes) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Understand that there is no rhyme or reason to the generator | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| Validate that the interface contains only necessary buttons. | 1 | 0 | 0 | min_k_enforced 1 | meetings 1 | qwen3.5-9b |
| Validate that the interface contains only the necessary buttons to score it as a one. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| Validate the button design to ensure it meets the 'necessary buttons only' criterion and gather final feedb... | 1 | 0 | 0 | max_k_shown 1 | meetings 1 | ministral-3-14b |
| Verify that the interface contains only the necessary buttons to meet user preferences. | 1 | 0 | 0 | min_k_shown 1 | meetings 1 | qwen3.5-9b |
| was Enron's building spared in the recent floods that we read about? (implicitly asking for information) - ... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Why did she have the section? (Note: This is a single request, but the schema requires at least 5 items. Si... | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| You gave me 2 invoices for CNR that are not on your April 2002 payment worksheet. Should I toss these 2 inv... | 1 | 0 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| } ``` (This is not a valid JSON instance either, but highlights the issue.) For a valid output, the documen... | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |

### Short, without those words: 317

| entry | times | rules say note | copied from the document | conditions | sets | models |
|---|---|---|---|---|---|---|
| List all the requests. | 26 | 0 | 0 | min_k_enforced 18, min_k_shown 8 | emails 26 | gemma-4-31b |
| TAX | 25 | 0 | 0 | min_k_enforced 18, min_k_shown 7 | receipts 25 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| Ilf | 23 | 0 | 0 | min_k_enforced 8, max_k_shown 6, min_k_shown 6, none 3 | wiki_people 23 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| warfarin | 23 | 0 | 20 | min_k_enforced 12, min_k_shown 5, max_k_shown 4, none 2 | clinical 23 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| Logistics | 20 | 0 | 18 | min_k_enforced 7, min_k_shown 7, max_k_shown 3, none 3 | job_posts_knowledge 20 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| Software Development | 20 | 0 | 19 | min_k_shown 7, min_k_enforced 6, max_k_shown 4, none 3 | job_posts_knowledge 20 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| he | 16 | 0 | 0 | min_k_enforced 11, max_k_shown 2, min_k_shown 2, none 1 | wiki_people 16 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| SQL | 16 | 0 | 0 | min_k_enforced 6, max_k_shown 4, min_k_shown 4, none 2 | job_posts_knowledge 16 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| 0 | 14 | 0 | 0 | max_k_shown 5, min_k_shown 4, min_k_enforced 3, none 2 | receipts 14 | qwen3.5-9b |
| enzyme technologies | 13 | 0 | 0 | min_k_enforced 5, min_k_shown 5, max_k_shown 2, none 1 | job_posts_knowledge 11, job_posts 2 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| coding | 11 | 0 | 0 | min_k_enforced 4, min_k_shown 4, max_k_shown 2, none 1 | job_posts_knowledge 11 | ministral-3-14b, qwen3.5-9b |
| project management | 10 | 0 | 0 | min_k_enforced 4, min_k_shown 3, max_k_shown 2, none 1 | job_posts_knowledge 10 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| get me college | 9 | 0 | 0 | min_k_shown 5, min_k_enforced 4 | emails 9 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| get me degree | 9 | 0 | 0 | min_k_shown 5, min_k_enforced 4 | emails 9 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| 1 | 8 | 0 | 0 | min_k_enforced 5, min_k_shown 3 | receipts 8 | ministral-3-14b, qwen3.5-9b |
| animal health monitoring | 8 | 0 | 0 | min_k_enforced 3, min_k_shown 2, max_k_shown 2, none 1 | job_posts_knowledge 8 | ministral-3-14b, qwen3.5-9b |
| DPP | 8 | 0 | 0 | min_k_enforced 6, min_k_shown 2 | receipts 8 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| Pb1 | 8 | 0 | 0 | min_k_enforced 6, min_k_shown 2 | receipts 8 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| Anne Westfall | 7 | 0 | 0 | min_k_shown 2, min_k_enforced 2, max_k_shown 2, none 1 | wiki_people 7 | qwen3.5-9b |
| CKM | 7 | 0 | 0 | min_k_shown 2, min_k_enforced 2, max_k_shown 2, none 1 | receipts 7 | qwen3.5-9b |
| animal feeding | 6 | 0 | 0 | min_k_shown 2, min_k_enforced 2, none 1, max_k_shown 1 | job_posts_knowledge 6 | ministral-3-14b |
| organizational skills | 6 | 0 | 0 | min_k_shown 2, max_k_shown 2, min_k_enforced 1, none 1 | job_posts_knowledge 6 | ministral-3-14b |
| team collaboration | 6 | 0 | 0 | min_k_enforced 2, min_k_shown 2, max_k_shown 1, none 1 | job_posts_knowledge 5, job_posts 1 | ministral-3-14b |
| warehouse operations | 6 | 0 | 0 | min_k_enforced 3, min_k_shown 3 | job_posts_knowledge 6 | gemma-4-31b, ministral-3-14b |
| adaptive environment | 5 | 0 | 0 | min_k_enforced 3, min_k_shown 2 | job_posts_knowledge 5 | gemma-4-31b, ministral-3-14b |
| complex systems | 5 | 0 | 0 | min_k_enforced 2, min_k_shown 2, max_k_shown 1 | job_posts_knowledge 5 | ministral-3-14b |
| excellent verbal communication skills | 5 | 0 | 0 | min_k_shown 2, none 2, max_k_shown 1 | job_posts 5 | ministral-3-14b, qwen3.5-9b |
| excellent written communication skills | 5 | 0 | 0 | min_k_shown 2, none 2, max_k_shown 1 | job_posts 5 | ministral-3-14b, qwen3.5-9b |
| His | 5 | 0 | 0 | min_k_enforced 3, min_k_shown 2 | wiki_people 5 | ministral-3-14b, qwen3.5-9b |
| Monitoring local government guidance | 5 | 0 | 0 | min_k_shown 2, min_k_enforced 2, none 1 | job_posts 5 | ministral-3-14b |
| portfolio development (complex sites) | 5 | 0 | 0 | max_k_shown 2, min_k_shown 2, none 1 | job_posts_knowledge 5 | ministral-3-14b |
| she | 5 | 0 | 0 | min_k_enforced 5 | wiki_people 5 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| Air | 4 | 0 | 0 | min_k_enforced 4 | wiki_people 4 | ministral-3-14b, qwen3.5-9b |
| animal movement | 4 | 0 | 0 | none 1, min_k_shown 1, max_k_shown 1, min_k_enforced 1 | job_posts_knowledge 4 | ministral-3-14b |
| Croissant Mini (NAM) 1x | 4 | 0 | 0 | min_k_shown 2, none 1, max_k_shown 1 | receipts 4 | ministral-3-14b |
| cross-cultural communication | 4 | 0 | 0 | min_k_enforced 2, none 1, min_k_shown 1 | job_posts_knowledge 4 | ministral-3-14b |
| Effective oral communication | 4 | 0 | 0 | max_k_shown 2, min_k_shown 2 | job_posts 4 | qwen3.5-9b |
| Effective written communication | 4 | 0 | 0 | max_k_shown 2, min_k_shown 2 | job_posts 4 | qwen3.5-9b |
| Freeman Westfal l | 4 | 0 | 0 | max_k_shown 2, min_k_enforced 1, min_k_shown 1 | wiki_people 4 | gemma-4-31b |
| Have Luiz Maurer attend. | 4 | 0 | 0 | min_k_shown 2, max_k_shown 1, min_k_enforced 1 | emails 4 | ministral-3-14b, qwen3.5-9b |
| Have Mike Roan attend. | 4 | 0 | 0 | min_k_shown 2, max_k_shown 1, min_k_enforced 1 | emails 4 | ministral-3-14b, qwen3.5-9b |
| industrial performance improvement | 4 | 0 | 0 | min_k_enforced 3, min_k_shown 1 | job_posts 4 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| pdf | 4 | 0 | 0 | min_k_shown 2, min_k_enforced 2 | job_posts_knowledge 4 | gemma-4-31b |
| product development | 4 | 0 | 0 | min_k_shown 2, none 1, min_k_enforced 1 | job_posts_knowledge 4 | gemma-4-31b, ministral-3-14b |
| SB | 4 | 0 | 0 | min_k_enforced 2, max_k_shown 1, none 1 | receipts 4 | qwen3.5-9b |
| sow management | 4 | 0 | 0 | min_k_shown 2, none 1, min_k_enforced 1 | job_posts_knowledge 4 | ministral-3-14b |
| sustainability | 4 | 0 | 0 | min_k_shown 2, none 1, max_k_shown 1 | job_posts_knowledge 4 | ministral-3-14b |
| call after December 4 | 3 | 0 | 0 | min_k_shown 2, max_k_shown 1 | emails 3 | qwen3.5-9b |
| collaboration with content producers | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts_knowledge 3 | ministral-3-14b |
| continuous improvement | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts_knowledge 3 | ministral-3-14b |
| CV | 3 | 0 | 0 | none 1, min_k_shown 1, min_k_enforced 1 | job_posts_knowledge 3 | gemma-4-31b, ministral-3-14b |
| digoxin | 3 | 0 | 0 | min_k_enforced 2, min_k_shown 1 | clinical 3 | ministral-3-14b |
| End of day batches | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts 3 | ministral-3-14b |
| farm operations | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts_knowledge 3 | ministral-3-14b |
| furosemide | 3 | 0 | 0 | min_k_enforced 2, min_k_shown 1 | clinical 3 | ministral-3-14b |
| global community collaboration | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts_knowledge 3 | ministral-3-14b |
| independent work | 3 | 0 | 0 | min_k_enforced 3 | job_posts_knowledge 3 | ministral-3-14b, qwen3.5-9b |
| iSeries Menu | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts 3 | ministral-3-14b |
| jugular vein percutaneous puncture | 3 | 0 | 0 | min_k_enforced 3 | clinical 3 | ministral-3-14b, qwen3.5-9b |
| minItems | 3 | 0 | 0 | min_k_enforced 3 | receipts 2, novel_quotes 1 | ministral-3-14b, qwen3.5-9b |
| multidisciplinary teamwork | 3 | 0 | 0 | min_k_enforced 1, max_k_shown 1, none 1 | job_posts 3 | ministral-3-14b |
| order fulfillment | 3 | 0 | 0 | min_k_enforced 2, min_k_shown 1 | job_posts_knowledge 3 | gemma-4-31b, ministral-3-14b, qwen3.5-9b |
| our | 3 | 0 | 0 | min_k_enforced 3 | wiki_people 3 | ministral-3-14b, qwen3.5-9b |
| passion for work | 3 | 0 | 0 | min_k_shown 2, min_k_enforced 1 | job_posts 2, job_posts_knowledge 1 | ministral-3-14b |
| professional growth | 3 | 0 | 0 | min_k_shown 3 | job_posts 2, job_posts_knowledge 1 | ministral-3-14b |
| provide the curve | 3 | 0 | 0 | min_k_shown 1, min_k_enforced 1, max_k_shown 1 | emails 3 | qwen3.5-9b |
| provide the requested information | 3 | 0 | 0 | min_k_shown 2, min_k_enforced 1 | emails 3 | gemma-4-31b |
| remote work | 3 | 0 | 1 | min_k_enforced 3 | job_posts 2, job_posts_knowledge 1 | qwen3.5-9b |
| software architecture | 3 | 0 | 0 | min_k_shown 1, none 1, min_k_enforced 1 | job_posts_knowledge 3 | ministral-3-14b |
| startup environment | 3 | 0 | 0 | min_k_shown 1, none 1, min_k_enforced 1 | job_posts_knowledge 3 | ministral-3-14b |
| talent acquisition | 3 | 0 | 0 | min_k_shown 2, min_k_enforced 1 | job_posts 3 | ministral-3-14b |
| talk to him | 3 | 0 | 0 | min_k_enforced 3 | emails 3 | ministral-3-14b, qwen3.5-9b |
| teamwork | 3 | 0 | 0 | min_k_shown 2, none 1 | job_posts_knowledge 2, job_posts 1 | ministral-3-14b |
| Unknown Person 2 | 3 | 0 | 0 | min_k_enforced 3 | wiki_people 3 | gemma-4-31b |
| Unknown Person 3 | 3 | 0 | 0 | min_k_enforced 3 | wiki_people 3 | gemma-4-31b |
| Unknown Person 4 | 3 | 0 | 0 | min_k_enforced 3 | wiki_people 3 | gemma-4-31b |
| Why? | 3 | 0 | 0 | min_k_enforced 2, min_k_shown 1 | novel_quotes 3 | gemma-4-31b |
| : 5, | 2 | 0 | 0 | min_k_enforced 2 | receipts 2 | ministral-3-14b |
| 500 | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | qwen3.5-9b |
| 7/7 | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | ministral-3-14b |
| agricultural labor | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| agricultural yield enhancement | 2 | 0 | 0 | min_k_enforced 2 | job_posts 2 | ministral-3-14b, qwen3.5-9b |
| animal castration | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| animal insemination | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| ATP | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | qwen3.5-9b |
| BI | 2 | 0 | 0 | min_k_enforced 2 | job_posts 2 | qwen3.5-9b |
| biotechnology | 2 | 0 | 0 | min_k_shown 2 | job_posts_knowledge 2 | ministral-3-14b |
| By | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | ministral-3-14b, qwen3.5-9b |
| CNV | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | qwen3.5-9b |
| Collaboration with multidisciplinary teams | 2 | 0 | 0 | min_k_shown 1, min_k_enforced 1 | job_posts 2 | ministral-3-14b |
| contact Dr. Tom Limperis | 2 | 0 | 0 | min_k_shown 1, min_k_enforced 1 | emails 2 | ministral-3-14b |
| description | 2 | 0 | 0 | min_k_enforced 2 | receipts 2 | ministral-3-14b |
| Effective oral communication skills | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | job_posts 2 | ministral-3-14b, qwen3.5-9b |
| enzymology | 2 | 0 | 0 | min_k_shown 2 | job_posts_knowledge 2 | ministral-3-14b |
| financial performance analysis | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| Freeman Westfal | 2 | 0 | 0 | min_k_shown 1, min_k_enforced 1 | wiki_people 2 | gemma-4-31b |
| front-end layer development | 2 | 0 | 0 | min_k_shown 1, none 1 | job_posts 2 | ministral-3-14b |
| Functional Materials knowledge | 2 | 0 | 0 | max_k_shown 1, none 1 | job_posts 2 | ministral-3-14b |
| get the requested information | 2 | 0 | 0 | min_k_enforced 2 | emails 2 | qwen3.5-9b |
| growth mindset | 2 | 0 | 0 | min_k_shown 1, none 1 | job_posts_knowledge 2 | ministral-3-14b |
| high-speed work culture | 2 | 0 | 0 | min_k_shown 1, none 1 | job_posts_knowledge 2 | ministral-3-14b |
| impact-driven work | 2 | 0 | 0 | min_k_shown 1, none 1 | job_posts_knowledge 2 | ministral-3-14b |
| incorporate some editorial changes | 2 | 0 | 0 | min_k_enforced 2 | emails 2 | qwen3.5-9b |
| industrial machinery | 2 | 0 | 0 | min_k_shown 1, none 1 | job_posts_knowledge 2 | ministral-3-14b |
| intercultural communication | 2 | 0 | 0 | min_k_shown 1, min_k_enforced 1 | job_posts_knowledge 2 | gemma-4-31b |
| intubation | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | ministral-3-14b |
| iv | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | qwen3.5-9b |
| marine applications | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| metoprolol | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | clinical 2 | ministral-3-14b |
| mg | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | qwen3.5-9b |
| night shift work | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| OCT | 2 | 0 | 0 | min_k_enforced 2 | clinical 2 | qwen3.5-9b |
| online application system | 2 | 0 | 0 | min_k_enforced 2 | job_posts_knowledge 2 | ministral-3-14b, qwen3.5-9b |
| Partnering with medical advisors | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | job_posts 2 | ministral-3-14b |
| PDP | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | ministral-3-14b, qwen3.5-9b |
| provide help | 2 | 0 | 0 | none 1, min_k_enforced 1 | emails 2 | gemma-4-31b, qwen3.5-9b |
| provide the required information | 2 | 0 | 0 | min_k_shown 1, min_k_enforced 1 | emails 2 | gemma-4-31b |
| renewable fuel development | 2 | 0 | 0 | min_k_enforced 2 | job_posts 2 | ministral-3-14b, qwen3.5-9b |
| resource preservation | 2 | 0 | 0 | min_k_enforced 2 | job_posts 2 | ministral-3-14b, qwen3.5-9b |
| spironolactone | 2 | 0 | 0 | min_k_enforced 1, min_k_shown 1 | clinical 2 | ministral-3-14b |
| stable maintenance | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| string | 2 | 0 | 0 | min_k_enforced 2 | receipts 2 | ministral-3-14b |
| The | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | ministral-3-14b |
| TV | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | ministral-3-14b, qwen3.5-9b |
| TV content delivery | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| type | 2 | 0 | 0 | min_k_enforced 2 | receipts 2 | ministral-3-14b |
| U.S. | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | qwen3.5-9b |
| Unknown Person 5 | 2 | 0 | 0 | min_k_enforced 2 | wiki_people 2 | gemma-4-31b |
| user experience (UX) | 2 | 0 | 0 | none 1, min_k_shown 1 | job_posts_knowledge 2 | ministral-3-14b |
| Verbal English comprehension | 2 | 0 | 0 | min_k_shown 2 | job_posts_knowledge 2 | ministral-3-14b, qwen3.5-9b |
| water | 2 | 0 | 1 | min_k_enforced 2 | wiki_people 1, receipts 1 | ministral-3-14b, qwen3.5-9b |
| work eligibility in <LOCATION> | 2 | 0 | 0 | min_k_shown 1, none 1 | job_posts_knowledge 2 | ministral-3-14b |
| ):```json[ARGS]{ | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| 1+1 | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | qwen3.5-9b |
| 3 | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| achieving great results | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| achieving results | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| ACTH replacement | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| adaptability | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| adaptive environments | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| agile methodologies | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| agile methodology | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| agile teamwork | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| analgesics (for headache, implied) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| anti-tussive medication | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antibiotics (unspecified) (used unsuccessfully) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antiemetics (for nausea/vomiting, implied) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| antihypertensives | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Appreciate the forward | 1 | 0 | 0 | max_k_shown 1 | emails 1 | ministral-3-14b |
| Ask about interview scheduling, | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Ask about relocation assistance, | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| attend the conference call | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Ben | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| bronchodilator | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| building better lives | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | qwen3.5-9b |
| business growth | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| business growth strategies | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| business strategy | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| calcitonin | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| Cardiac medication (unspecified) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| career advancement | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| catheter (balloon delivery system) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Charles Wick | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | ministral-3-14b |
| cinacalcet | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| COFFEE | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| Collaborating with medical advisors | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | ministral-3-14b |
| Collaboration in person | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | qwen3.5-9b |
| Collaboration with external stakeholders | 1 | 0 | 0 | none 1 | job_posts 1 | ministral-3-14b |
| complex system architecture | 1 | 0 | 0 | max_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Conducting remote video interviews | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| confirm the termination decision | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| contact Joe D | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| cortisol replacement | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| cough suppressant | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| customer service (industrial/marine context) | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| daily task variation | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| data analytics solutions | 1 | 0 | 0 | none 1 | job_posts 1 | ministral-3-14b |
| DAX | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | qwen3.5-9b |
| denosumab | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| designing Power BI reports | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | ministral-3-14b |
| DESSERT | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| device flexibility | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| dexamethasone implant | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| digital streaming | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | gemma-4-31b |
| diuretics | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| diuretics (e.g., furosemide) | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| diversity and inclusion | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| diversity and inclusiveness | 1 | 0 | 0 | min_k_enforced 1 | job_posts_knowledge 1 | gemma-4-31b |
| driving license (valid) | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| dynamic work environment | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Effective written communication skills | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | qwen3.5-9b |
| empowerment | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| end | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | ministral-3-14b |
| end user consumption analysis | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | ministral-3-14b |
| engineering maintenance | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| error | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| evaluate the provided forecasts | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| everolimus (10 mg daily) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| execute GSA | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| expectorant | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| F.J. | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | qwen3.5-9b |
| feeding and moving animals | 1 | 0 | 0 | max_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| flexible work environments | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| flexible working environments | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| fluid dynamics | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| forward GSA to Jode | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| founder interaction | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| founders' direct access | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| GD | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| glucocorticoid replacement therapy | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| go to dinner together | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| GYM | 1 | 0 | 0 | min_k_enforced 1 | job_posts_knowledge 1 | qwen3.5-9b |
| hand scanner usage | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Have fun (Scotty) | 1 | 0 | 0 | none 1 | emails 1 | ministral-3-14b |
| HBV | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| heat transfer technology | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| hemoptysis management (unspecified) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| Hepatitis C | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | gemma-4-31b |
| high-speed work | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| I | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | ministral-3-14b |
| i.v. | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| immunosuppressants | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| impact-driven roles | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Includes some editorial changes. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| incorporates some editorial changes | 1 | 0 | 0 | min_k_shown 1 | emails 1 | gemma-4-31b |
| INR | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| insulin (for diabetes mellitus) | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| international team collaboration | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Interview process participation | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | qwen3.5-9b |
| Kim. | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| Knowledge on .NET Core | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | qwen3.5-9b |
| learning environment | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| Les | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | qwen3.5-9b |
| livestock handling | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| livestock management | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| logistics (spare parts distribution) | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| marine engineering | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Materials research expertise | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| mechanical systems | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| medication1 | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| medication2 | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| medication3 | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| medication4 | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| medication5 | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| medications_mentioned: false | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| microbial biotechnology | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| microbiology | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| neurogenic bladder medications | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| night shifts | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| offshore applications | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| offshore engineering | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| On-line application systems | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | gemma-4-31b |
| Order in for dinner | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| ownership in roles | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| parathyroid adenoma treatment | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| parathyroid carcinoma treatment | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| parathyroid hormone (PTH) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| parathyroid hyperplasia management | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| parathyroidectomy (surgical intervention) | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| partner establishment (professional clout) | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| passion | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| Pat! | 1 | 0 | 0 | min_k_enforced 1 | novel_quotes 1 | gemma-4-31b |
| PDF file formatting | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| PDF file submission | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| personal development | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| personal growth | 1 | 0 | 0 | min_k_shown 1 | job_posts 1 | ministral-3-14b |
| planetary resource preservation | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| Please provide more information | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| Please send the plat | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| portfolio development | 1 | 0 | 0 | min_k_enforced 1 | job_posts_knowledge 1 | ministral-3-14b |
| prednisone | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| provide a resume | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| provide comments | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| Provide data requirements | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| provide feedback | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| provide tariff sheets | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| reason: none_in_text | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| regulatory compliance (industrial/marine standards) | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Remote collaboration | 1 | 0 | 0 | max_k_shown 1 | job_posts 1 | ministral-3-14b |
| Request a response deadline, | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| Request feedback on qualifications, | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| review RESUME3.doc | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| review the attached Guaranty | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| review the maps | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | gemma-4-31b |
| Rigiflex® (pneumatic dilatation balloon) | 1 | 0 | 0 | min_k_shown 1 | clinical 1 | ministral-3-14b |
| safety protocols (marine/offshore) | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| SANDWICH | 1 | 0 | 0 | min_k_enforced 1 | receipts 1 | ministral-3-14b |
| send my resume | 1 | 0 | 0 | max_k_shown 1 | emails 1 | qwen3.5-9b |
| sigmoidoscope (endoscopic device) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| sports streaming | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| stable maintenance (lights) | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| streaming platforms | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| submit the compiled form | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| supply chain management | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| supportive therapies (unspecified) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| supportive work environments | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| sustainable industrial practices | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| system architecture | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | qwen3.5-9b |
| talent management | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| team autonomy | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| team ownership | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| teamwork and cooperation | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| technical documentation | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| technical troubleshooting | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| thyroid medication (methimazole) | 1 | 0 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| trust | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| Unknown Person 1 | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | gemma-4-31b |
| user experience (UX) design | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| values alignment | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| Verbal English | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| weekend work | 1 | 0 | 0 | none 1 | job_posts_knowledge 1 | ministral-3-14b |
| Working with external stakeholders | 1 | 0 | 0 | max_k_shown 1 | job_posts 1 | ministral-3-14b |
| workplace motivation | 1 | 0 | 0 | min_k_shown 1 | job_posts_knowledge 1 | ministral-3-14b |
| write back | 1 | 0 | 0 | min_k_enforced 1 | emails 1 | qwen3.5-9b |
| writing DAX queries | 1 | 0 | 0 | min_k_enforced 1 | job_posts 1 | ministral-3-14b |
| Z | 1 | 0 | 0 | min_k_enforced 1 | wiki_people 1 | qwen3.5-9b |
| Zero! fingertip | 1 | 0 | 0 | min_k_enforced 1 | novel_quotes 1 | gemma-4-31b |

## Already treated as notes: 43 distinct entries

| entry | times | rules say note | copied from the document | conditions | sets | models |
|---|---|---|---|---|---|---|
| No people mentioned in the text | 77 | 77 | 0 | min_k_enforced 77 | wiki_people 77 | gemma-4-31b |
| not mentioned | 47 | 47 | 0 | min_k_enforced 47 | clinical 37, wiki_people 10 | gemma-4-31b, qwen3.5-9b |
| none | 37 | 37 | 0 | min_k_enforced 37 | clinical 37 | qwen3.5-9b |
| No quotations found in the provided text. | 36 | 36 | 0 | min_k_enforced 36 | novel_quotes 36 | gemma-4-31b |
| None mentioned | 35 | 35 | 0 | min_k_enforced 35 | clinical 35 | gemma-4-31b |
| No medications mentioned | 23 | 23 | 0 | min_k_enforced 23 | clinical 23 | gemma-4-31b, qwen3.5-9b |
| , | 15 | 15 | 0 | min_k_enforced 15 | meetings 9, clinical 5, receipts 1 | gemma-4-31b, ministral-3-14b |
| : [ | 14 | 14 | 0 | min_k_enforced 14 | clinical 11, receipts 2, emails 1 | ministral-3-14b |
| medications | 11 | 11 | 0 | min_k_enforced 11 | clinical 11 | ministral-3-14b |
| The provided text contains no direct speech. | 6 | 6 | 0 | min_k_enforced 6 | novel_quotes 6 | gemma-4-31b |
| line_items | 5 | 5 | 0 | min_k_enforced 5 | receipts 5 | ministral-3-14b |
| No medications listed. | 5 | 5 | 0 | min_k_enforced 5 | clinical 5 | ministral-3-14b, qwen3.5-9b |
| None mentioned in the text | 5 | 5 | 0 | min_k_enforced 5 | clinical 5 | gemma-4-31b |
| Not found | 5 | 5 | 0 | min_k_enforced 5 | emails 5 | gemma-4-31b |
| No drugs listed | 4 | 4 | 0 | min_k_enforced 4 | clinical 4 | qwen3.5-9b |
| No requests found in text. | 4 | 4 | 0 | min_k_enforced 4 | emails 4 | gemma-4-31b |
| "--" | 3 | 3 | 0 | max_k_shown 2, none 1 | novel_quotes 3 | ministral-3-14b |
| N/A | 3 | 3 | 0 | min_k_enforced 3 | receipts 3 | gemma-4-31b |
| No medications mentioned in the provided text | 3 | 3 | 0 | min_k_enforced 3 | clinical 3 | gemma-4-31b |
| No medications mentioned in the text | 3 | 3 | 0 | min_k_enforced 3 | clinical 3 | gemma-4-31b |
| None specified. | 3 | 3 | 0 | min_k_enforced 3 | clinical 3 | ministral-3-14b |
| unknown | 3 | 3 | 0 | min_k_enforced 3 | wiki_people 2, clinical 1 | gemma-4-31b, qwen3.5-9b |
| items | 2 | 2 | 0 | min_k_enforced 2 | receipts 2 | ministral-3-14b |
| Person 2 | 2 | 2 | 0 | min_k_enforced 2 | wiki_people 2 | gemma-4-31b |
| Person 3 | 2 | 2 | 0 | min_k_enforced 2 | wiki_people 2 | gemma-4-31b |
| Person 4 | 2 | 2 | 0 | min_k_enforced 2 | wiki_people 2 | gemma-4-31b |
| Person 5 | 2 | 2 | 0 | min_k_enforced 2 | wiki_people 2 | gemma-4-31b |
| requests | 2 | 2 | 0 | min_k_enforced 2 | emails 2 | ministral-3-14b |
| *No additional requests found in the provided document* | 1 | 1 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| medications: [ | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| nil | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| No additional requests found in the provided email. | 1 | 1 | 0 | min_k_shown 1 | emails 1 | ministral-3-14b |
| No drug information available | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| No drug names provided. | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| No further action is required at this time. | 1 | 1 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| No items are listed for the recipient to do or provide. | 1 | 1 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| No medications listed in the provided patient history. | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| No over-the-counter drugs mentioned. | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| No requests are explicitly stated in the provided document. | 1 | 1 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| None mentioned in the document. | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | qwen3.5-9b |
| Not specified | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
| The document does not contain any actionable requests. | 1 | 1 | 0 | min_k_enforced 1 | emails 1 | ministral-3-14b |
| The document does not mention any medications taken by the patient. | 1 | 1 | 0 | min_k_enforced 1 | clinical 1 | ministral-3-14b |
