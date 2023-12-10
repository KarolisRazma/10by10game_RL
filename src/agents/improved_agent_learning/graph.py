import src.agents.improved_agent_learning.queries as QUERIES
import src.game_components.chip as cp
from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.game_components.game_result import GameResult
from src.game_components.state_data import StateData
from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData


# Structure of the graph
#
# node GameState:
#   property: board_values
#   property: my_turn
#   property: my_score
#   property: enemy_score
#   property: chips_left
#   property: last_placed_chip [row, col, value]
#   property: hand_chips_values
#   property: enemy_hand_chips_values
#   property: container_chip_values
#   property: is_initial
#   property: is_final
#   property: is_closed (optional)
#
# relation NEXT
#   property: row
#   property: col
#   property: chip_value
#   property: has_taking
#   property: combination [Chip, Chip, ...]
#   property: times_used (optional)
#   property: win_counter (optional)
#   property: lose_counter (optional)
#   property: draw_counter (optional)
#   property: q_value (optional)
#   property: from_closed_state (optional)

class Graph:
    def __init__(self, session):
        self.session = session

    # Delete entire db
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)

    def find_or_create_final_state(self, state_data: ImprovedAgentStateData):
        params = {
            "board_values": state_data.board_values,
            "my_turn": state_data.my_turn,
            "my_score": state_data.my_score,
            "enemy_score": state_data.enemy_score,
            "chips_left": state_data.chips_left,

            "last_placed_chip": state_data.last_placed_chip_list,
            "hand_chips_values": state_data.hand_chips_values_list,
            "enemy_hand_chips_values": state_data.enemy_hand_chips_values_list,
            "container_chips_values": state_data.container_chips_values_list,

            "is_initial": state_data.is_initial,
            "is_final": state_data.is_final,
        }
        self.session.run(QUERIES.FIND_OR_CREATE_FINAL_STATE, **params)

    def find_or_create_previous_state_and_make_next_relation(self,
                                                             previous_state_data: ImprovedAgentStateData,
                                                             relation_data: ImprovedAgentActionData,
                                                             current_state_data: ImprovedAgentStateData,
                                                             game_result: GameResult,
                                                             to_closed_state=False):
        combination_integer_list = []
        for chip in relation_data.combination:
            combination_integer_list.append(chip.row)
            combination_integer_list.append(chip.col)
            combination_integer_list.append(chip.value)

        params = {
            "p_board_values": previous_state_data.board_values,
            "p_my_turn": previous_state_data.my_turn,
            "p_my_score": previous_state_data.my_score,
            "p_enemy_score": previous_state_data.enemy_score,
            "p_chips_left": previous_state_data.chips_left,
            "p_is_initial": previous_state_data.is_initial,
            "p_is_final": previous_state_data.is_final,
            "p_last_placed_chip": previous_state_data.last_placed_chip_list,
            "p_hand_chips_values": previous_state_data.hand_chips_values_list,
            "p_enemy_hand_chips_values": previous_state_data.enemy_hand_chips_values_list,
            "p_container_chips_values": previous_state_data.container_chips_values_list,
            "c_board_values": current_state_data.board_values,
            "c_my_turn": current_state_data.my_turn,
            "c_my_score": current_state_data.my_score,
            "c_enemy_score": current_state_data.enemy_score,
            "c_chips_left": current_state_data.chips_left,
            "c_is_initial": current_state_data.is_initial,
            "c_is_final": current_state_data.is_final,
            "c_last_placed_chip": current_state_data.last_placed_chip_list,
            "c_hand_chips_values": current_state_data.hand_chips_values_list,
            "c_enemy_hand_chips_values": current_state_data.enemy_hand_chips_values_list,
            "c_container_chips_values": current_state_data.container_chips_values_list,
            "row": relation_data.row,
            "col": relation_data.col,
            "chip_value": relation_data.chip_value,
            "has_taking": relation_data.has_taking,
            "combination": combination_integer_list,
            "q_value": relation_data.q_value,
            "to_closed_state": to_closed_state
        }
        if game_result == GameResult.WON:
            self.session.run(QUERIES.FIND_OR_CREATE_PREVIOUS_STATE_AND_MAKE_NEXT_RELATION_WHEN_WIN, **params)
        elif game_result == GameResult.LOST:
            self.session.run(QUERIES.FIND_OR_CREATE_PREVIOUS_STATE_AND_MAKE_NEXT_RELATION_WHEN_LOSE, **params)
        elif game_result == GameResult.DRAW:
            self.session.run(QUERIES.FIND_OR_CREATE_PREVIOUS_STATE_AND_MAKE_NEXT_RELATION_WHEN_DRAW, **params)

    def find_game_state_next_relations(self, state_data: StateData):
        params = {
            "board_values": state_data.board_values,
            "my_turn": state_data.my_turn,
            "my_score": state_data.my_score,
            "enemy_score": state_data.enemy_score,
            "chips_left": state_data.chips_left,
            "is_initial": state_data.is_initial,
            "is_final": state_data.is_final,
            "last_placed_chip": state_data.last_placed_chip_list,
            "hand_chips_values": state_data.hand_chips_values_list,
            "enemy_hand_chips_values": state_data.enemy_hand_chips_values_list,
            "container_chips_values": state_data.container_chips_values_list
        }
        result = self.session.run(QUERIES.FIND_GAME_STATE_NEXT_RELATIONS, **params)
        records = list(result)
        updated_records = []
        for record in records:
            rel_properties = record["r"]._properties
            updated_records.append(self.make_improved_agent_action_data_from_record(rel_properties))
        return updated_records

    def find_max_next_state_q_value(self, state_data):
        relations_info = self.find_game_state_next_relations(state_data)
        result = (max(relations_info, key=lambda x: x.q_value)).q_value
        return result

    # Only used in state closing (DO NOT USE ANYWHERE ELSE)
    def find_or_create_next_game_state_and_make_rel(self, current_state_data: ImprovedAgentStateData,
                                                    relation_data: ImprovedAgentActionData,
                                                    next_state_data: ImprovedAgentStateData):
        combination_integer_list = []
        for chip in relation_data.combination:
            combination_integer_list.append(chip.row)
            combination_integer_list.append(chip.col)
            combination_integer_list.append(chip.value)
        params = {
            "c_board_values": current_state_data.board_values,
            "c_my_turn": current_state_data.my_turn,
            "c_my_score": current_state_data.my_score,
            "c_enemy_score": current_state_data.enemy_score,
            "c_chips_left": current_state_data.chips_left,
            "c_is_initial": current_state_data.is_initial,
            "c_is_final": current_state_data.is_final,
            "c_last_placed_chip": current_state_data.last_placed_chip_list,
            "c_hand_chips_values": current_state_data.hand_chips_values_list,
            "c_enemy_hand_chips_values": current_state_data.enemy_hand_chips_values_list,
            "c_container_chips_values": current_state_data.container_chips_values_list,
            "n_board_values": next_state_data.board_values,
            "n_my_turn": next_state_data.my_turn,
            "n_my_score": next_state_data.my_score,
            "n_enemy_score": next_state_data.enemy_score,
            "n_chips_left": next_state_data.chips_left,
            "n_is_initial": next_state_data.is_initial,
            "n_is_final": next_state_data.is_final,
            "n_last_placed_chip": next_state_data.last_placed_chip_list,
            "n_hand_chips_values": next_state_data.hand_chips_values_list,
            "n_enemy_hand_chips_values": next_state_data.enemy_hand_chips_values_list,
            "n_container_chips_values": next_state_data.container_chips_values_list,
            "row": relation_data.row,
            "col": relation_data.col,
            "chip_value": relation_data.chip_value,
            "has_taking": relation_data.has_taking,
            "combination": combination_integer_list,
            "from_closed_state": True
        }
        self.session.run(QUERIES.FIND_OR_CREATE_NEXT_GAME_STATE_AND_MAKE_REL, **params)

    def close_game_state(self, state_data: ImprovedAgentStateData):
        params = {
            "board_values": state_data.board_values,
            "my_turn": state_data.my_turn,
            "my_score": state_data.my_score,
            "enemy_score": state_data.enemy_score,
            "chips_left": state_data.chips_left,
            "last_placed_chip": state_data.last_placed_chip_list,
            "hand_chips_values": state_data.hand_chips_values_list,
            "enemy_hand_chips_values": state_data.enemy_hand_chips_values_list,
            "container_chips_values": state_data.container_chips_values_list,
            "is_initial": state_data.is_initial,
            "is_final": state_data.is_final,
            "is_closed": state_data.is_closed
        }
        self.session.run(QUERIES.CLOSE_GAME_STATE, **params)

    @staticmethod
    def make_improved_agent_action_data_from_record(relation_properties):
        row = relation_properties['row']
        col = relation_properties['col']
        chip_value = relation_properties['chip_value']

        improved_agent_action_data = ImprovedAgentActionData(row, col, chip_value)

        improved_agent_action_data.has_taking = relation_properties['has_taking']

        if 'combination' in relation_properties.keys():
            combination_integer_list = relation_properties['combination']
            time_iterate = int(len(combination_integer_list) / 3)
            for i in range(time_iterate):
                chip = cp.Chip(combination_integer_list[3 * i + 2])
                chip.row = combination_integer_list[3 * i + 0]
                chip.col = combination_integer_list[3 * i + 1]
                improved_agent_action_data.combination.append(chip)

        if 'from_closed_state' in relation_properties.keys():
            improved_agent_action_data.from_closed_state = relation_properties['from_closed_state']
        if 'to_closed_state' in relation_properties.keys():
            improved_agent_action_data.to_closed_state = relation_properties['to_closed_state']
        if 'q_value' in relation_properties.keys():
            improved_agent_action_data.q_value = relation_properties['q_value']
        if 'times_used' in relation_properties.keys():
            improved_agent_action_data.times_used = relation_properties['times_used']
        if 'win_counter' in relation_properties.keys():
            improved_agent_action_data.win_counter = relation_properties['win_counter']
        if 'lose_counter' in relation_properties.keys():
            improved_agent_action_data.lose_counter = relation_properties['lose_counter']
        if 'draw_counter' in relation_properties.keys():
            improved_agent_action_data.draw_counter = relation_properties['draw_counter']

        return improved_agent_action_data

    # NOT USED ATM
    # @staticmethod
    # def make_improved_agent_state_data_from_record(record):
    #     # TODO: The question is do I need all of these? (I mean always?)
    #     board_values = record['board_values']
    #     my_turn = record['my_turn']
    #     my_score = record['my_score']
    #     enemy_score = record['enemy_score']
    #     chips_left = record['chips_left']
    #     last_placed_chip_list = record['last_placed_chip']
    #     hand_chips_values_list = record['hand_chips_values']
    #     enemy_hand_chips_values_list = record['enemy_hand_chips_values']
    #     container_chips_values_list = record['container_chips_values']
    #     is_initial = record['is_initial']
    #     is_final = record['is_final']
    #
    #     improved_agent_state_data = ImprovedAgentStateData(
    #         board_values=board_values,
    #         my_turn=my_turn,
    #         my_score=my_score,
    #         enemy_score=enemy_score,
    #         chips_left=chips_left,
    #         last_placed_chip_list=last_placed_chip_list,
    #         hand_chips_values_list=hand_chips_values_list,
    #         enemy_hand_chips_values_list=enemy_hand_chips_values_list,
    #         container_chips_values_list=container_chips_values_list,
    #         is_initial=is_initial,
    #         is_final=is_final
    #     )
    #     return improved_agent_state_data
