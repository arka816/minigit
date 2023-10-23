import hashlib
import os

class FileTreeNode:
    '''
        implementation of a minigit filetree object
    '''
    def __init__(self, children : list["FileTreeNode"], path : str, is_blob : bool) -> None:
        self.children = children
        self.path = path
        self.is_blob = is_blob

        self.calculate_hash()
    
    def calculate_hash(self) -> None:
        '''
            calculate SHA-1 hash using hashes of the children objects or of the file object if it is a blob
        '''

        if self.is_blob:
            with open(self.path, 'rb') as f:
                digest = hashlib.file_digest(f, 'sha1')
                self.content_hash = digest.hexdigest()
        else:
            hash = hashlib.sha1()

            for child in self.children:
                child.calculate_hash()
                hash.update(bytes.fromhex(child.content_hash))

            self.hash = hash.hexdigest()


def create_file_tree_recursive(cwd):
    '''
        scour the current working directory recursively
        and form the file tree
    '''
    children = []
    for child_file in os.listdir(cwd):
        child_file_path = os.path.join(cwd, child_file)

        child_node = None

        if os.path.isfile(child_file_path):
            child_node = FileTreeNode([], child_file_path, True)
        elif os.path.isdir(child_file_path):
            child_node = create_file_tree_recursive(child_file_path)
        
        if child_node is not None:
            children.append(child_node)

    node = FileTreeNode(children, cwd, False)
    return node
