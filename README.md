# Notes

|
Some inspiration taken from a defunct project here: https://github.com/rfk/dexml/blob/master/dexml/__init__.py

# References


http://opendocumentformat.org/developers/
https://github.com/csev/gift2qti

#Using the model to convert from and to

The base model is an item which stores internal information (structural info like title, description) 
and information on disk (mostly files).
What we need is to have a generic model that would account for most of the course structures (in Moodle, edX, IMS
Content packages).
For example 

|   ODP Document            |       EZ Disteach Internal Model   |          IMS Content Package                 |
|---------------------------|------------------------------------|----------------------------------------------|
|   Slideshow               |      Course (title, description, language...)   |    The whole package metadata   |
|   A slide from the slideshow   |      Course Section(title,description)   |    An item (metadata) without IdentifierRef   |
|   A bullet point (level 1) in a slide   |      Item(title, description, content)   |    An item (metadata) with IdentifierRef and ressources attached   |

Question now will be to create an API that would allow different input and output as a result.

## Tablib as an example
A good inspiration is coming from tablib in python who allows to convert in and out just
by setting or getting a dynamic properties and duck typing a dataset into an array.

### Example:

Setup the data as an array (duck typing):


    headers = ('first_name', 'last_name')
    data = [
        ('John', 'Adams'),
        ('George', 'Washington')
    ]
    
    data = tablib.Dataset(*data, headers=headers)
    data[0] = ('Jo', 'Down')
    data.append(('New', 'Row'))
    data.headers = ['First', 'Second']



Exporting :


    # To text
    print (data.csv)  # Print data as csv
    print (data.export('csv'))
    # Via streams, csv_module being a format in tablib
    csv_stream = csv_module.export_stream_set(data)
    # Or
    data.load(stream, 'csv')
    


Importing :

    data = tablib.Dataset()    
    data.csv  = csvrawdata
    data.set_csv(csvrawdata, delimiter=';')


## Components

So we have a base model which represents the structure of a course. A course can be splitted into finer granular
items such as:

* Sections (a group of items)
* Items (a single activity)

We can imagine also that section can contain other sections and so on.

Each element of the model will be based on a "Base model". The base model is an item that has the capability to 
be structured into a tree so has:
* A parent (can be empty)
* A list of children
* Structural data such as uid, title, description...
* A file or a series of binary files attached to it (this is opaque to the structure/model)
* other metadata such as uid (generated)

So the entity can be split in:
* its structure (the tree, the metadata like title and so on)
* its attached binary content

For each model (course, section, item (quiz,discussion, binaryfile, htmlfile)) we have a
consistent set of methods:

##File API


Files are attached to a model/item, so they are quite important to store apart. The model
will have a different set of metadata and a unique identifier.
Each file will be served by a file entity which will have several methods/properties:
 - file.name = the current filename (basename)
 - file.vfs = virtual file system where the file is stored
 - file.path = path where the file is stored, root is VFS
 - file.stream = a file stream to read or write (if write, then it will be the same as the constructor
 method)

## For input:


Load the model and relevant files from a stream (autodetect the input format):

``
    course = ezdisteach.Course()
    course.load(open('inputfilename', 'rb'),'odp')   
``

Just link the file to model and load it in the VFS. It will set its filename and
its path will be just under the item unique identifier:

``
    model.file = './filepath'
``

If you need to change its path, better is to set the path thereafter:

``
    file.path = path where the file is stored, root is VFS
``

The vfs should be is a shared ressource between the different entities in the tree so
whenever an entity file is created the vfs for the file will be taken from its
parent if it exists.
 
We can optionally (and this is internally used) just load the metadata from a file:

``
model.meta = open('inputfilename','r') # Load metadata from a file (mostly xml)
``

### Summary:

The we can have specific filters:
model.stream # Parse content of file
model.file #  will return the file stream or set the file and upload it in the VDS
model.file.name  # Will just get or update the filename (and change its name on VFS)
model.file.path = # will set or return the file path in the VFS (change its path)
 
## Specialisation : Load the content from a file from ODP 

Load the ODP file with all the content (.odp is a stream):

``
course.odp = ODPfile  
``

We could have done with autodetection:

``
course.stream = ODPFile
``

To just load the metadata, i.e. course structure (title, lom, ...):

``
course.odp.meta = <odp file>  
``

This will create empty sections and items with their metadata through similar methods in
subitems such as:

``
course.section[1].odp.meta = <odp file > 
``

Which will load the metadata of the section from the odp file. As there is no file attached
to a section, there is no need ot add the call to

`` 
course.section[1].file = <filepath>
``

However for an item such as a PDF, the process would be as follow.


    bfile = BinaryFile()
    bfile.file = <filepath> 
    bfile.name = 'filename.pdf'
    bfile.title = "This is a pdf document"


Note that is means that the BinaryFile class is both a File (as a VFS file) and an item as
it has also additional metadata such as title.

Very similarly for any type of item in the course:

``
course.section[1].item[1].odp.meta = odp file
``

This will create the relevant item (quiz, file, discussion)
Basically .odp, will call first odp_meta and create the relevant entity if necessary, i.e.:
 - File if this is a generic binary file (PDF), then it will call item.file = <file>
 - Discussion if this is a discussion
 - Quiz if it is a quiz

So the general process for odb:

course.odp calls course.odp.meta to get definition for the course. For each item it
will call their internal method odp.meta to create the tree like structure. The files
 if any will be attached to the entity through the item.file method.

### Caching ?
Note that later we will need a cache system to avoid duplicating the opening / parsing of
the ODP file

## Output

For output, we will have different choices from simple flat file to a folder like structure
like IMS Content packages, Moodle archive or edX archive.

The output process will be quite similar to the input.

course.imscc will return a streamed file which will contain both the metadata and the files from
its content.
We will also have a method called metadata for imscc that will return either a full xml document
or a fragment of an xml document (or several documents).
 
course.imscc => Streams a full IMSCC package (*.imscc)
course.imscc.meta => Streams the full imsmanifest.xml

For sub entities, the stream method is not that relevant as it will return only unuseable bits.
However, we can stream the attached file by doing for example for a pdf entity.
pdf.stream => will return a filestream pointing to the content of the file
pdf.imscc.meta.item => will return a fragment of XML with the item tag
pdf.imscc.meta.resource => will return a fragment of XML with the resource tag

