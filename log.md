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
6. Print the decoded mode, the type of file (blob, tree, etc), the decrypted 20 byte sha and the name of the file.
6. Skip the following 20 characters from the data and repeat from **step 3** until there are no more characters