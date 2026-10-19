# Windows Control Panel

This branch adds an experimental Tkinter Windows control panel around the existing `main.py` automation core.

## Build

Run the GitHub Actions workflow **Build DeltaForceSS Windows EXE** manually, or push changes to this branch. Download the `DeltaForceSS-Windows` artifact from the completed run.

## First run

1. Extract the artifact into a plain-English path.
2. Keep `DeltaForceSS.exe`, `config.yaml`, and `user_config.yaml` in the same folder.
3. Install Tesseract OCR and set `TESSERACT_PATH` in `user_config.yaml` to the actual `tesseract.exe` path.
4. Open the game at the Special Forces Department crafting screen, then launch the panel.

## Mandatory automatic-selling safety policy

**Only items positively confirmed as produced and collected by this program may ever be sold.**

- Do not sell an item just because its name matches a configured production target or because it appears in the warehouse.
- A future implementation must record each production job and only add an item to the eligible ledger after the existing workflow positively confirms successful completion and collection.
- At sale time, inventory recognition must match eligible records by item identity and available quantity. Ambiguous OCR, missing records, name collisions, quantity mismatches, or uncertain state mean **skip the item**.
- Items not made by this program, manually acquired items, and any item whose origin cannot be proven are never eligible.
- The initial implementation must show a reviewable sale preview and require explicit user confirmation. Automated selling must remain disabled until the ledger and inventory matching have been tested.
- Never infer eligibility from configured targets alone. A target is not proof that an item was actually produced.

## Current limitations

- The panel can launch and stop the existing automation worker and display its log.
- The existing core still controls mouse/keyboard and depends on supported 16:9 resolutions.
- Automatic selling is not implemented. The panel explicitly marks it disabled until production provenance tracking, inventory recognition, sell-page navigation, and safeguards can be validated.
- This is an experimental build; verify it in a safe test scenario before leaving it unattended.
