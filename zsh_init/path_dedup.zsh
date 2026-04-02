# Function to add to PATH without duplicates
path_prepend() {
    case ":$PATH:" in
        *":$1:"*) ;;
        *) export PATH="$1:$PATH" ;;
    esac
}

path_append() {
    case ":$PATH:" in
        *":$1:"*) ;;
        *) export PATH="$PATH:$1" ;;
    esac
}

# Function to remove duplicates from PATH
dedup_path() {
    local new_path=""
    local IFS=':'
    for dir in $PATH; do
        case ":$new_path:" in
            *":$dir:"*) ;;
            *) new_path="${new_path:+$new_path:}$dir" ;;
        esac
    done
    export PATH="$new_path"
}
