# Record
REC_INDEX_ID = (0, "id")
REC_INDEX_NAME = (1, "name")
REC_INDEX_DATE = (2, "date")
REC_INDEX_DATE_INT = (3, "date_int")
REC_INDEX_BODY = (4, "body")
REC_INDEX_DRAFT = (5, "draft")
REC_INDEX_CREATED_AT = (6, "created_at")
REC_INDEX_UPDATED_AT = (7, "updated_at")
REC_INDEX_BODY_HTML = (8, "body_html")
REC_INDEX_TAGS = (9, "tags") # Added filed, does not exist in database
REC_INDEX_IMAGES = (10, "images") # Added filed, does not exist in database
REC_INDEX_FILES = (11, "files") # Added filed, does not exist in database
# Record data
REC_DATA_INDEX_ID = (0, "id")
REC_DATA_INDEX_RECORD_ID = (1, "record_id")
REC_DATA_INDEX_TAG_ID = (2, "tag_id")
REC_DATA_INDEX_MEDIA_ID = (3, "media_id")
# Tag
TAG_INDEX_ID = (0, "id")
TAG_INDEX_NAME = (1, "name")
TAG_INDEX_USER_DEF = (2, "user_def")
TAG_INDEX_DESC = (3, "desc")
# Image
IMG_INDEX_ID = (0, "id")
IMG_INDEX_NAME = (1, "name")
IMG_INDEX_DESC = (2, "desc")
IMG_INDEX_FILE = (3, "file")
IMG_INDEX_HTTP = (4, "http")
IMG_INDEX_IS_DEFAULT = (5, "is_default")
# File
FILE_INDEX_ID = (0, "id")
FILE_INDEX_NAME = (1, "name")
FILE_INDEX_DESC = (2, "desc")
FILE_INDEX_FILE = (3, "file")
FILE_INDEX_HTTP = (4, "http")
FILE_INDEX_IS_DEFAULT = (5, "is_default")
# Definition
DEF_INDEX_ID = (0, "id")
DEF_INDEX_NAME = (1, "name")
DEF_INDEX_DESC = (2, "desc")
DEF_INDEX_EXPRESSIONS = (4, "expressions") # Added filed, does not exist in database
DEF_INDEX_IMAGES = (5, "images") # Added filed, does not exist in database
DEF_INDEX_DEFAULT_IMAGE = (6, "def_image") # Added filed, does not exist in database

# Other constants
SAVED_FLAG = "is_saved"
PERCENT_FEEDBACK_STEP = 7

