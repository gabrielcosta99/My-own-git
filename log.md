## First Exercise
Iniating the repository. No big deal here

## Second Exercise: git cat-file
git cat-file is used to view the type of an object, its size, and its content. Example usage:

```sh  
$ git cat-file -p <blob_sha>
hello world # This is the contents of the blob
```

**I only implement the `git cat-file -p`**

The order of the steps are:
1. Read the contents of the blob object file from the `.git/objects` directory
2. Decompress the contents using Zlib
3. Extract the actual "content" from the decompressed data
4. Print the content to stdout


## Third Exercise: git hash-object

`git hash-object` is used to compute the SHA hash of a Git object. When used with the -w flag, it also writes the object to the .git/objects directory.

Here's an example of using git hash-object:
```sh
  # Create a file with some content
  $ echo "hello world" > test.txt

  # Compute the SHA hash of the file + write it to .git/objects
  $ git hash-object -w test.txt
  3b18e512dba79e4c8300dd08aeb37f8e728b8dad

  # Verify that the file was written to .git/objects
  $ file .git/objects/3b/18e512dba79e4c8300dd08aeb37f8e728b8dad
  .git/objects/3b/18e512dba79e4c8300dd08aeb37f8e728b8dad: zlib compressed data
```

**I only implemented the `git hash-object -w`**

To implement it i did the following:
1. Convert the file into a blob, after Zlib decompression (`blob <size>\0<content>`)
2. Compress the blob using zlib
3. Hash the blob
4. Create the directory, in which the file will be stored (if necessary)
4. Write the data **(the compressed blob)** to the appropriate file in `.git/objects` **(the hashed blob)**
5. Print the hashed blob to the console

## Fourth Exercise: Read a tree object (ls-tree)

The `git ls-tree` command is used to inspect a tree object.
For a directory structure like this:
```
your_repo/
  - file1
  - dir1/
    - file_in_dir_1
    - file_in_dir_2
  - dir2/
    - file_in_dir_3
```
The output of git ls-tree would look like this:

```sh
$ git ls-tree <tree_sha>
040000 tree <tree_sha_1>    dir1
040000 tree <tree_sha_2>    dir2
100644 blob <blob_sha_1>    file1
```
Note that the output is alphabetically sorted, this is how Git stores entries in the tree object internally.

### Tree objects:

The format of a tree object file looks like this (after Zlib decompression):
```
tree <size>\0
<mode> <name>\0<20_byte_sha>
<mode> <name>\0<20_byte_sha>
```
(The above code block is formatted with newlines for readability, but the actual file doesn't contain newlines)

### Implementing 'ls-tree --name-only'
To do this I followed the following steps:
1. Zlib decompress the file
2. Remove the header 
3. Split the data by the first `b"\0"` that appears (`line` and `data` where the variables I used)
4. Split the first part by the `space character` and print the second element 
5. Remove the first 20 characters from `data` since we won't be using the hash
6. Repeat from **step 3** until no elements remain

### optional: implementing 'ls-tree'
To do this I followed the following steps:
1. Zlib decompress the file
2. Remove the header 
3. Split the data by the first `b"\0"` that appears (`line` and `data` where the variables I used)
4. Split the first part by the `space character` (resulting in the `mode` and `name` variables)
5. Decrypt the first 20 characters using `sha1` 
6. Check what type of file it is (directory, file, symbolic link)
7. Print the decoded mode, the type of file (blob, tree, etc), the decrypted 20 byte sha and the name of the file.
8. Skip the following 20 characters from the data and repeat from **step 3** until there are no more characters


## Fifth Exercise: Write tree objects (write-tree)
**In this exercise, i won't be using a staging area, I'll just assume that all files are staged.**
The `git write-tree` command creates a tree object from the current state of the "staging area". The staging area is a place where changes go when you run git add.

Here's an example of using git write-tree:
```sh
  # Create a file with some content
  $ echo "hello world" > test.txt

  # Add the file to the staging area (we won't implement a staging area in this challenge)
  $ git add test.txt

  # Write the tree to .git/objects
  $ git write-tree
  4b825dc642cb6eb9a060e54bf8d69288fbee4904
```
The output of git write-tree is the 40-char SHA hash of the tree object that was written to `.git/objects`.

To implement this, I needed to:
1. Iterate over the files/directories in the working directory
2. If the entry is a file, create a blob object (using the same logic as `hash-object`) and record its SHA hash
3. If the entry is a directory, recursively create a tree object and record its SHA hash
4. Once you have all the entries and their SHA hashes, write the tree object to the .git/objects directory
5. If you're testing this against git locally, make sure to run git add . before git write-tree, so that all files in the working directory are staged.

**Note:** remember that a tree object is something like this:
```
  tree <size>\0
  <mode> <name>\0<20_byte_sha>
  <mode> <name>\0<20_byte_sha>
```
and the mode is:
- `100755` for executable files
- `100644` for regular files
- `040000` for directories

## Sixth Exercise: Create a commit (commit-tree)

A commit has the following format: `commit {size}\0{content}`, where `{content}` is:
```
tree {tree_sha}
{parents}
author {author_name} <{author_email}> {author_date_seconds} {author_date_timezone}
committer {committer_name} <{committer_email}> {committer_date_seconds} {committer_date_timezone}

{commit message}
```

where:
- `{tree_sha}`: SHA of the tree object this commit points to.

  This represents the top-level Git repo directory.

- `{parents}`: optional list of parent commit objects of form:
  ```
    parent {parent1_sha}
    parent {parent2_sha}
    ...
  ```
  The list can be empty if there are no parents, e.g. for the first commit in a repo.

  Two parents happen in regular merge commits.

  More than two parents are possible with git merge -Xoctopus, but this is not a common workflow. Here is an example: https://github.com/cirosantilli/test-octopus-100k

- `{author_name}`: e.g.: `Ciro Santilli`. Cannot contain `<`, `\n`

- `{author_email}`: e.g.: `cirosantilli@mail.com`. Cannot contain `>`, `\n`

- `{author_date_seconds}`: seconds since 1970, e.g. `946684800` is the first second of year 2000

- `{author_date_timezone}`: e.g.: ` +0000` is UTC

- committer fields: analogous to author fields

- `{commit message}`: arbitrary .


## Seventh Exercise: Clone a repository

I used [this](https://stefan.saasen.me/articles/git-clone-in-haskell-from-the-bottom-up/#reimplementing-git-clone-in-haskell-from-the-bottom-up) website to understand better how does the `git clone` works: text


