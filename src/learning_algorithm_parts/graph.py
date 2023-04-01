from neo4j import GraphDatabase
import src.game_components.actions.placing_action as pan

# Database Credentials
uri = "bolt://localhost:7687"
userName = "neo4j"
password = "password"


class Graph:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri, auth=(userName, password))
        self.driver.verify_connectivity()
        self.session = self.driver.session()

    # ADD NEW VERTICES
    def add_n_board_states(self, current_state_values, next_state_values_list, action_type, actions, placed_chip):
        for (next_state_values, action) in zip(next_state_values_list, actions):
            self.add_board_state(current_state_values, next_state_values, action_type, action, placed_chip)

    def add_board_state(self, current_state_values, next_state_values, action_type, action, placed_chip):
        # Create vertex
        result = self.session.run(
            "MERGE (:BoardState {board_values: $board_values})",
            board_values=next_state_values
        )

        # If not root element
        if current_state_values is not None:
            # Create relation for placing
            if action_type == "placing":
                result = self.session.run(
                    """ MATCH (curr:BoardState {board_values: $c_board_values})
                        MERGE (next:BoardState {board_values: $n_board_values})
                        MERGE (curr)-[:NEXT {action_type: $action_type, row: $row, col: $col, value: $value}]->(next) 
                    """, c_board_values=current_state_values, n_board_values=next_state_values, action_type=action_type,
                    row=action.row, col=action.col, value=action.value
                )
            # Create relation for taking
            else:
                updated_action = []
                for chip in action:
                    updated_action.append(chip.row)
                    updated_action.append(chip.col)
                    updated_action.append(chip.value)

                result = self.session.run(
                    """ MATCH (curr:BoardState {board_values: $c_board_values})
                        MERGE (next:BoardState {board_values: $n_board_values})
                        MERGE (curr)-[:NEXT {action_type: $action_type, combination: $combination, placed_chip: $placed_chip}]->(next) 
                    """, c_board_values=current_state_values, n_board_values=next_state_values,
                    action_type=action_type, combination=updated_action, placed_chip=placed_chip
                )

    # GET VERTEX
    def find_board_state(self, board_values):
        result = self.session.run(
            """ MATCH (boardState:BoardState)
                WHERE boardState.board_values = $board_values
                RETURN boardState 
            """, board_values=board_values
        )
        record = result.single(strict=True)
        return record

    # GET GIVEN VERTEX NEXT VERTICES
    def find_board_state_next_vertices(self, parent_state_values):
        result = self.session.run(
            """ MATCH (parentState:BoardState)-[:NEXT]->(childState:BoardState)
                WHERE parentState.board_values = $parent_state_values
                RETURN childState
            """, parent_state_values=parent_state_values
        )
        records = list(result)
        # Parse records to list of ints
        updated_records = []
        for record in records:
            updated_records.append(record.data()['childState']['board_values'])
        return updated_records

    # GET ACTION FROM PARENT TO CHILD VERTEX
    def find_next_action(self, parent_state_values, child_state_values, action_type, board):
        if action_type == "placing":
            result = self.session.run(
                """ MATCH (parentState:BoardState)-[r]->(childState:BoardState)
                    WHERE parentState.board_values = $parent_state_values AND childState.board_values = $child_state_values
                    RETURN r.row, r.col, r.value
                """, parent_state_values=parent_state_values, child_state_values=child_state_values
            )
            record = result.single(strict=True).data()
            row = int(record['r.row'])
            col = int(record['r.col'])
            value = int(record['r.value'])
            return pan.PlaceChipAction(row, col, value)
        if action_type == "taking":
            result = self.session.run(
                """ MATCH (parentState:BoardState)-[r]->(childState:BoardState)
                    WHERE parentState.board_values = $parent_state_values AND childState.board_values = $child_state_values
                    RETURN r.combination
                """, parent_state_values=parent_state_values, child_state_values=child_state_values
            )
            # record = result.single(strict=True).data()
            # combination = record['r.combination']
            # RETURNS list of chips row/col/value to remove

            records = list(result)
            if len(records) > 1:
                print(f'Before: {parent_state_values}')
                print(f'After: {child_state_values}')
                print("Comb")
                for record in records:
                    print(record.data()['r.combination'])
            combination = records[0].data()['r.combination']

            return combination

    # RETURNS BOARD VALUES OF ALL VERTICES
    def get_everything(self):
        result = self.session.run("MATCH (bs:BoardState) RETURN bs.board_values AS board_values")
        records = list(result)  # a list of Record objects
        return records

    # RETURNS TRUE IF VERTEX IS FOUND
    def is_vertex_found(self, board_values):
        result = self.session.run(
            """ MATCH (boardState:BoardState {board_values: $board_values})
                WITH COUNT(boardState) > 0  as node_exists
                RETURN node_exists
            """, board_values=board_values
        )
        return result.single(strict=True).data()['node_exists']

    # DELETE ENTIRE DB
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)
