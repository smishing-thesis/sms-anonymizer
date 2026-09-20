# Single source of truth for the scam/ham labeling scheme, used by both the
# Excel dropdown (export) and the label validation (import).
LABEL_TO_INT = {"scam": 1, "ham": 0}
ALLOWED_LABELS = tuple(LABEL_TO_INT)
