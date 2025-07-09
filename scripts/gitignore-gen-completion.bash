#!/bin/bash
# Bash completion script for gitignore-gen

_gitignore_gen_completion() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    cmds="templates scan version"
    
    # Options
    opts="--verbose --quiet --dry-run --interactive --backup --security --monorepo --help --version"
    
    # Template-specific options
    template_opts="--template --output"
    
    # Scan-specific options
    scan_opts="--path"
    
    case "${prev}" in
        gitignore-gen)
            if [[ ${cur} == * ]] ; then
                COMPREPLY=( $(compgen -W "${cmds} ${opts}" -- "${cur}") )
            fi
            ;;
        templates)
            if [[ ${cur} == * ]] ; then
                COMPREPLY=( $(compgen -W "${template_opts} --help" -- "${cur}") )
            fi
            ;;
        scan)
            if [[ ${cur} == * ]] ; then
                COMPREPLY=( $(compgen -W "${scan_opts} --help" -- "${cur}") )
            fi
            ;;
        --template|-t)
            # Common template names
            templates="python node java go rust swift csharp php ruby dart kotlin scala django flask fastapi react vue angular spring laravel rails maven gradle webpack vite rollup vscode intellij eclipse vim emacs macos windows linux unity unreal docker kubernetes terraform jest cypress playwright"
            COMPREPLY=( $(compgen -W "${templates}" -- "${cur}") )
            ;;
        --path|-p)
            # Directory completion
            COMPREPLY=( $(compgen -d -- "${cur}") )
            ;;
        --output|-o)
            # File completion
            COMPREPLY=( $(compgen -f -- "${cur}") )
            ;;
        *)
            if [[ ${cur} == * ]] ; then
                COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
            fi
            ;;
    esac
}

complete -F _gitignore_gen_completion gitignore-gen 