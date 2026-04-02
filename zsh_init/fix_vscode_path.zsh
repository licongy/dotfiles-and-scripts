#!/usr/bin/env zsh

# Complete VSCode PATH fix - Reset and rebuild PATH from scratch
# This file should be sourced at the very beginning of .zshenv

# Only run this fix in VSCode terminal
if [[ "$TERM_PROGRAM" == "vscode" ]]; then
    # Save the original PATH for debugging
    export VSCODE_ORIGINAL_PATH="$PATH"
    
    # Reset PATH to system defaults only
    export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    
    # Add Homebrew paths (if homebrew is installed)
    if [[ -d "/opt/homebrew" ]]; then
        export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
    fi
    
    # Add other system paths that might be needed
    if [[ -d "/System/Cryptexes/App/usr/bin" ]]; then
        export PATH="$PATH:/System/Cryptexes/App/usr/bin"
    fi
    
    # Mark that we've reset the PATH
    export VSCODE_PATH_RESET=1
fi
