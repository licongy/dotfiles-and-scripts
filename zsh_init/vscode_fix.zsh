# VSCode Terminal Fix
# This file helps prevent duplicate PATH entries in VSCode integrated terminal

# Check if we're running in VSCode terminal
if [[ "$TERM_PROGRAM" == "vscode" ]]; then
    # Mark that we've already initialized for VSCode
    if [[ -z "$VSCODE_ZSH_INIT_DONE" ]]; then
        export VSCODE_ZSH_INIT_DONE=1
    else
        # If we've already initialized, skip shell config loading
        return 0
    fi
fi

# Additional safeguard: track which files have been sourced
typeset -gA SOURCED_FILES
SOURCED_FILES[zshenv]=1
SOURCED_FILES[zprofile]=1
SOURCED_FILES[zshrc]=1
