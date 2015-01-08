from zipfile import ZipFile, is_zipfile
import hashlib
import argparse
import sys
import os
from collections import defaultdict, Counter
from itertools import combinations


class zipentry():
    """
    Wrapper Object for File Metadata.
    """
    def __init__(self, name, hash, file):
        self.name = name
        self.hash = hash
        self.file = file
        self.references = set()
    
    
    def __str__(self):
        return "%s:%s in %s%s" % (self.name, self.hash, self.file, "" if len(self.references) == 0 else " referenced by %s" % (", ".join([x.file for x in self.references])))
        
    
    def addReference(self, zipentry):
        self.references.add(zipentry)
        
    
    def hasReference(self):
        return len(self.references) != 0
        
        
    def inAll(self):
        # check first if there are any references
        if not self.hasReference():
            return False
            
        # check first if there is any copied file in both sets
        copy_found = False
        for reference in self.references:
            if self.file == reference.file and self.hash == reference.hash:
                copy_found = True
        if copy_found:
            # now we need to check if the copy is in both files
            edges = {}
            to_check = list(self.references)
            
            while len(to_check) > 0:
                reference = to_check.pop()
                if reference not in edges.keys():
                    edges[reference] = list(reference.references)
                    to_check.extend(list(reference.references))
            
            # create a list of all nodes
            nodes = set([node for l in edges.values() for node in l])
            
            copy = True
            # now iterate over all node -> edges pairs and see if they are the same as the nodes set
            for n, e in edges.items():
                c = set(e) | set([n])
                if nodes != c:
                    copy = False
            
            # if we found out that these copies are allover the same, return True
            if copy:
                return True
            
        
        for reference in self.references:
            # check if a reference is in the same file and has same hash --> copied file
            if (self.file == reference.file and self.hash == reference.hash):
                continue
                
            # check if the reference in another file is same name and hash
            if (self.hash != reference.hash or self.name != reference.name):
                return False
            
        return True

        
def main():
    parser = argparse.ArgumentParser(description='Diff ZIP Files')
    parser.add_argument('zipfile', nargs=2, help='The Files to Diff')
    parser.add_argument("-a", dest="a", action="store_true", default=True, help="Use File A as reference. (default)")
    parser.add_argument("-b", dest="b", action="store_true", default=False, help="Use File B as reference.")
    
    # TODO
    parser.add_argument("--deleted", action="store_true", default=False)
    parser.add_argument("--added", action="store_true", default=False)
    parser.add_argument("--changed", action="store_true", default=False)
    parser.add_argument("--renamed", action="store_true", default=False)
    parser.add_argument("--same", action="store_true", default=False)
    parser.add_argument("--all", action="store_true", default=False)

    args = parser.parse_args()
    
    # global namelist
    filelist = []

    for f in args.zipfile:
        # just ignore the fact that it maybe isnt a zip file...
        try:
            with ZipFile(f) as zf:
                for name in zf.namelist():
                    hash = hashlib.md5(zf.read(name)).hexdigest()
                    
                    filelist.append(zipentry(name, hash, os.path.basename(f)))
        except:
            print("[ERROR] while processing file %s" %f)
            
    reference = os.path.basename(args.zipfile[0]) if args.a and not args.b else os.path.basename(args.zipfile[1])
    
    print("Comparing %s (Reference set to %s)" % (" and ".join(args.zipfile), reference))
    print()
            

    # compare all files and store references to each other
    for a, b in combinations(filelist, 2):
        if a.name == b.name:
            a.addReference(b)
            b.addReference(a)
            
        if a.hash == b.hash:
            a.addReference(b)
            b.addReference(a)    

    if args.deleted:
        # print all deleted files
        print("List of files that are deleted in file B")
        
        for file in filelist:
            if not file.inAll():
                print(file)
    
    if args.added:
        # print all added files
        pass
    
    if args.changed:
        # print all changed files
        pass
        
    if args.renamed:
        # print all renamed files
        pass
        
    if args.same:
        # print all non-changed files
        print("List of Files that are the same in both files")
        for file in filelist:
            if file.inAll() and file.file == reference:
                print(file)

                   
            
if __name__ == "__main__":
    main()