'''
    implementation of a local Repo object

    handles operations
        - create
        - index 
        - sync

'''

import os

from filetree import create_file_tree_recursive

class Local:
    '''
        wrapper class for all local operations
    '''

    def __init__(self) -> None:
        self.working_dir = os.getcwd()
        self.local_dir = os.path.join(self.working_dir, '.minigit')

    def create_repo(self) -> None:
        '''
            - create necessary folder structure for minigit
            - generate file blobs
            - create file tree
        '''

    def create_file_tree(self) -> None:
        '''
            create a file tree object
            save the root node
        '''
        self.file_tree_root = create_file_tree_recursive(self.working_dir)
