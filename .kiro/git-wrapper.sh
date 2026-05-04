#!/bin/bash
# Git wrapper that blocks --no-verify flag
# This provides TRUE enforcement because it intercepts BEFORE git sees the command
#
# BACKGROUND: Using --no-verify bypasses Code Defender security hooks and triggers
# corporate security alerts. This got Jim in trouble. NEVER AGAIN.
#
# Usage: Source this file to override the git command
#   source .kiro/git-wrapper.sh
#
# Or add to your shell profile (~/.bashrc, ~/.zshrc):
#   source /path/to/Home-Automation/.kiro/git-wrapper.sh

git() {
    # Check for forbidden flags in all arguments
    for arg in "$@"; do
        if [[ "$arg" == "--no-verify" || "$arg" == "-n" ]]; then
            echo ""
            echo "🚨 ════════════════════════════════════════════════════════════════"
            echo "🚨  ERROR: --no-verify flag is BLOCKED by enterprise policy"
            echo "🚨 ════════════════════════════════════════════════════════════════"
            echo ""
            echo "  This flag bypasses Code Defender security hooks."
            echo "  Using it triggers corporate security alerts."
            echo ""
            echo "  Jim got in trouble last time this was used."
            echo "  DO NOT BYPASS SECURITY HOOKS. EVER."
            echo ""
            echo "  If hooks are failing, FIX THE UNDERLYING ISSUE."
            echo "  Ask Jim for help if needed."
            echo ""
            echo "🚨 ════════════════════════════════════════════════════════════════"
            echo ""
            return 1
        fi
    done
    
    # If clean, run real git
    command git "$@"
}

# Export the function so it's available in subshells
export -f git

echo "✓ Git security wrapper loaded - --no-verify flag will be blocked"
