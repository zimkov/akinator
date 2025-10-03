

class TreeNode:
    def __init__(self, question=None):
        self.question = question
        self.left = None
        self.right = None

    def add_child(self, direction, child):
        """Добавление дочернего узла"""
        if direction == 'left':
            self.left = child
        elif direction == 'right':
            self.right = child

    def to_db(self, db: TreeDB):
        """Сериализация дерева в БД"""
        node_id = db.add_node(self.question)

        if not self.left and not self.right:
            # Листья (животное)
            db.set_leaf(node_id, self.question)  # Пока не реализовано
            return node_id

        left_id = self.left.to_db(db) if self.left else None
        right_id = self.right.to_db(db) if self.right else None

        db.cursor.execute('''
            UPDATE nodes SET 
                left_child_id = ?, 
                right_child_id = ?
            WHERE id = ?
        ''', (left_id, right_id, node_id))
        db.conn.commit()

        return node_id
