# Windows Control Panel

This branch adds an experimental Tkinter control panel around the existing `main.py` automation core.

## Build

Run the GitHub Actions workflow **Build DeltaForceSS Windows EXE** manually, or push changes to this branch. Download the `DeltaForceSS-Windows` artifact from the completed run.

## First run

1. Extract the artifact into a plain-English path.
2. Keep `DeltaForceSS.exe`, `config.yaml`, and `user_config.yaml` in the same folder.
3. Install Tesseract OCR and set `TESSERACT_PATH` in `user_config.yaml` to the actual `tesseract.exe` path.
4. Open the game at the Special Forces Department crafting screen, then launch the panel.

## Current limitations

- The panel can launch and stop the existing automation worker and display its log.
- The existing core still controls mouse/keyboard and depends on supported 16:9 resolutions.
- Automatic selling is not implemented. The panel explicitly marks it disabled until inventory recognition, sell-page navigation, and price/whitelist safeguards can be validated.
- This is an experimental build; verify it in a safe test scenario before leaving it unattended.
