#!/bin/bash
# OKPy deployment helper — images live on GCS (ok-project-assets/okpy).
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="${PROJECT_NAME:-okpy}"
SERVICE_URL="${SERVICE_URL:-https://okpy.net}"
GCS_BUCKET="${GCS_BUCKET:-gs://ok-project-assets/${PROJECT_NAME}}"
POSTS_IMAGES="${POSTS_IMAGES:-app/static/images/posts}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-starful-258005}"

MODE="full"
DO_GIT=false
DO_CLOUD_DEPLOY=false

print_step() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}
print_ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
print_info() { echo -e "  ℹ️  $1"; }

usage() {
    cat <<'EOF'
Usage: ./deploy.sh [MODE] [OPTIONS]

Modes (default: full)
  --full           Sync/upload post images to GCS
  --content-only   No-op placeholder (markdown is source of truth)
  --deploy-only    Trigger Cloud Build deploy only

Options
  --with-git       Commit and push changes
  --with-deploy    Trigger deploy after selected mode
  --help           Show this help

Environment overrides
  PROJECT_NAME     Default: okpy
  SERVICE_URL      Default: https://okpy.net
  GCS_BUCKET       Default: gs://ok-project-assets/${PROJECT_NAME}
  POSTS_IMAGES     Default: app/static/images/posts
  GCP_PROJECT_ID   Default: starful-258005
EOF
}

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Missing required command: $1" >&2
        exit 1
    fi
}

sync_cloud_images_to_local() {
    print_step "STEP A: Cloud -> Local post images"
    mkdir -p "$POSTS_IMAGES"
    gcloud storage rsync "$GCS_BUCKET" "$POSTS_IMAGES" --recursive --project="$GCP_PROJECT_ID"
    print_ok "Cloud image sync completed"
}

upload_images_to_gcs() {
    print_step "STEP B: Local -> GCS post images"
    if [ ! -d "$POSTS_IMAGES" ]; then
        print_info "No local posts images directory; skipping upload"
        return
    fi
    gcloud storage rsync "$POSTS_IMAGES" "$GCS_BUCKET" --recursive --checksums-only --project="$GCP_PROJECT_ID"
    # Public read (bucket may already allow this)
    gsutil -m acl ch -u AllUsers:R "$GCS_BUCKET/**" >/dev/null 2>&1 || true
    print_ok "GCS upload completed"
}

git_push_changes() {
    print_step "STEP C: Commit and push changes"
    git add .
    if ! git diff-index --quiet HEAD --; then
        local commit_msg
        commit_msg="chore: update okpy contents $(date '+%Y-%m-%d %H:%M')"
        git commit -m "$commit_msg"
        git push origin main
        print_ok "Git push completed"
    else
        print_info "No changes detected, skipping git push"
    fi
}

deploy_cloud_run() {
    print_step "STEP D: Trigger Cloud Build"
    gcloud builds submit --project "$GCP_PROJECT_ID" --config=cloudbuild.yaml .
    print_ok "Cloud Build deployment completed"
    gcloud run services add-iam-policy-binding okpy \
        --project="$GCP_PROJECT_ID" \
        --region=us-central1 \
        --member=allUsers \
        --role=roles/run.invoker >/dev/null 2>&1 || true
}

for arg in "$@"; do
    case "$arg" in
        --full) MODE="full" ;;
        --content-only) MODE="content-only" ;;
        --deploy-only) MODE="deploy-only" ;;
        --with-git) DO_GIT=true ;;
        --with-deploy) DO_CLOUD_DEPLOY=true ;;
        --help|-h) usage; exit 0 ;;
        *)
            echo "Unknown argument: $arg" >&2
            usage
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"
START_TIME=$SECONDS

print_info "Project: $PROJECT_NAME"
print_info "Service URL: $SERVICE_URL"
print_info "Mode: $MODE"
print_info "Bucket: $GCS_BUCKET"
print_info "GCP project: $GCP_PROJECT_ID"

require_cmd python3
require_cmd gcloud

case "$MODE" in
    full)
        require_cmd gsutil
        sync_cloud_images_to_local
        upload_images_to_gcs
        ;;
    content-only)
        print_info "Content-only: markdown already on disk; nothing to generate"
        ;;
    deploy-only)
        DO_CLOUD_DEPLOY=true
        ;;
esac

if [ "$DO_GIT" = true ]; then
    require_cmd git
    git_push_changes
fi

if [ "$DO_CLOUD_DEPLOY" = true ]; then
    deploy_cloud_run
fi

ELAPSED=$((SECONDS - START_TIME))
echo -e "\n${BOLD}${GREEN}Done in $((ELAPSED/60))m $((ELAPSED%60))s${NC}"
