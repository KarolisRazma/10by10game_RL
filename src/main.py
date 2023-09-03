from src.game_interface import GameInterface
import src.utilities.gi_constants as GI_CONSTANTS

if __name__ == "__main__":
    interface = GameInterface(GI_CONSTANTS.ENVIRONMENT_3X3)
    interface.show_initial_options()



