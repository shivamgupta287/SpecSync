from .log_config import setup_logging
setup_logging()

from .brands import get_all_brands, find_brand
from .phones import get_phones_for_brand
from .specs import search_phone, get_phone_specs
from .display import print_phone_list, print_specs
from .writer import save_to_json
