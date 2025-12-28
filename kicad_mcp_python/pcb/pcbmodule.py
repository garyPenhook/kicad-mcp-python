import logging

from kipy import KiCad
from kipy.proto.common.types import KIID

from ..utils.convert_proto import get_object_type

logger = logging.getLogger(__name__)


def detect_board_capabilities(board) -> dict[str, bool]:
    return {
        "get_items_by_id": callable(getattr(board, "get_items_by_id", None)),
    }

class PCBTool:
    """
    Represents a PCB module with its properties and methods.
    """

    def initialize_kicad(self):
        # TODO: Need to add logic to refresh the board.
        try:
            self.board = KiCad().get_board()
            self.board_capabilities = detect_board_capabilities(self.board)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize the board: {str(e)}")

    def get_item_by_id(self, item_type: str, item_id: str):
        if not hasattr(self, "board_capabilities"):
            self.board_capabilities = detect_board_capabilities(self.board)

        if self.board_capabilities.get("get_items_by_id"):
            try:
                kiid = KIID()
                kiid.value = item_id
                items = self.board.get_items_by_id([kiid])
                return items[0] if items else None
            except Exception:
                logger.debug("get_items_by_id failed; falling back to get_items", exc_info=True)

        item_dict = {
            item.id.value: item
            for item in self.board.get_items(get_object_type(item_type))
        }
        return item_dict.get(item_id)
