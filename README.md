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

## Tablib and lxml as examples
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

As per lxml:

    root = etree.Element("root")
    print (root.tag)
    root.append( etree.Element("child1") )
    child2 = etree.SubElement(root, "child2")
    child3 = etree.SubElement(root, "child3")
    print(etree.tostring(root, pretty_print=True))
    <root>
        <child1/>
        <child2/>
        <child3/>
    </root>
    # then we can access subelement via the array notation
    child =  root[0]
    print (child.tag)
    print (len(root))
    # Then for attributes, they are just a dict
    root = etree.Element("root", interesting="totally")
    print(root.get("interesting"))
        totally
    root.set("hello", "Huhu")
    # Then element have for example text inside (we would have binary files in our model)
    root = etree.Element("root")
    root.text = "TEXT
    
Exporting (tablib):


    # To text
    print (data.csv)  # Print data as csv
    print (data.export('csv'))
    # Via streams, csv_module being a format in tablib
    csv_stream = csv_module.export_stream_set(data)
    # Or
    data.load(stream, 'csv')
    


Importing (tablib):

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
* other metadata such as uid (generated), formatting

So the entity can be split in:
* its structure (the tree, the metadata like title and so on)
* its attached binary content

For each model (course, section, item (quiz,discussion, binaryfile, htmlfile)) we have a
consistent set of methods who will allow duck typing.

So the model will be a generic Item (or CourseModel), will have all necessary method to be used as an array for
its children (so as an array of Model(s)), get or set its attached files (via a specific attribute called files), 
format it into.



##File Types of Items

Files can be attached to Items. We could consider that they are a type of items too as they have both metadata (name,...)
and a binary content.
So we can build a specialized item which will store information about a file, let's call it BinaryFile.
Each file will be served by a file entity which will have several methods/properties:
 - ``file.name``  or ``file.meta.name`` = the current filename (basename)
 - ``file.vfs`` or ``file.meta.vfs`` = virtual file system where the file is stored
 - ``file.path`` or ``file.meta.path``= path where the file is stored, root is VFS
 - ``file.stream`` = a file stream to read or write the file from or the file to
   
## For input:

Load the a course and relevant files from a stream (autodetect the input format):

    course = ezdisteach.CourseModel('Course')
    course.load(open('myprescourse.odp', 'rb'),'odpcourse')
    # Or
    course.odpcourse.stream = <file> 
   

Load the a course and relevant files from a stream (autodetect the input format):

    course = ezdisteach.CourseModel('Course')
    course.append(ezdisteach.CourseModel('Section'))
    course[0].append(ezdisteach.CourseModel('HTMLContent')) # a specific item
    course[0][0].load(open('myprescourse.odp', 'rb'),'odpcourse')   # will load the matching slide item in the presentation
    # Or we could have done
    course[0][0].odpcourse.stream = open('myprescourse.odp', 'rb')

The model will have attributes and eventually files:

    course = ezdisteach.CourseModel('Course')
    course.title = 'My Course' # Same as course.meta.title
    course.description = 'My Course description \<p\>HTML\</p\>'
    
    course.append(eddisteach.CourseModel('BinaryFile',load('filename')) # will error out as we don't know where to put it
    item = ezdisteach.CourseModel('BinaryFile')
    item.stream = 'filename' # will add this file to the list of files for this item
    # we can then write the file out on a stream
   
   
Just load the course metadata and relevant files from a stream:

    course = ezdisteach.CourseModel('Course')
    course.meta.load('imsmanifest.xml','imscc')
    
    course = ezdisteach.CourseModel('Course')
    course.meta.load('mycourse.odp','odp')
    # Ou
    course.odpcourse.meta = open('mycourse.odp', 'rb')
    
It will create the relevant structure and entities. Files can then be attached later.


### Using and attaching files

The Binary File model will have a small file API that will allow to add new files. Each file will
have a name and a virtual path. 
The virtual path will be path in a virtual filesytem that will be rooted in the
item itself. The usual '../' path will be used to get to the parent's path. 
If the parent is not set this will error out.
Note that the append function will set the parent automatically.

citem.stream #  will return the file stream for the first attached file
citem.name  # Will return or set the filename
citem.path = 'filepath'  # Rooted in the item itself or '../filepath', rooted to the parent 


### Summary:

An item (being a BinaryFile, a Quiz, or a whole course) has the following capabilities:
* Load from a binary file via the ``.load(stream, filtername)`` or directly via ``.stream`` property (autodetection) or
finally with ``.<filtername>.stream``. This way will change the internal metadata of the item
* We can change the item metadata by accessing its properties directly or using the .meta property

**Exemples:**

* ``model.load('filename', 'formatname')`` parse content of file and update the model
* ``ezdisteach.CourseModel('Course')`` will create a course datamodel

An item can contain several items, for each of them:
* ``citem.meta`` will return the attached structure/metadata if it makes sense
* ``citem.stream``  will return the file stream if it makes sense. It will use the default filter
* ``citem.<filtername>.stream``  will return a stream or use a stream filter so to load the content in the item from 
a binary source
* ``citem.meta.uid`` will return a unique id as well as ``citem.uid``

For files for example:
* ``citem.meta.name``  or ``citem.name``  will return or set the filename
* ``citem.meta.path``  will return the file path relative to the item (local filepath) 

 
## Specialisation : Load the content from a file from ODP 

Load the ODP file with all the content (.odp is a stream), instead of load:

``
    course.odpcourse.stream = ODPfile  or stream
``

This will create the relevant section and subsection using the format converter for each
type. 


However for an item such as a PDF, the process would be as follow.


    bfile = ezdisteach.CourseModel('BinaryFile')
    bfile.meta.title = "This is a pdf document"
    bfile.stream = <filepath> or stream # (will load the file for later use)
    bfile.name = 'filename.pdf'
    bfile.path = '' # Rooted in the item itself


Loading an item from the ODP file can be done:

``
    course[1][1].odpcourse.stream = odp file 
``

This will do the following:

``course.__get_item__(course,0).__get_item__(section,0).load(odpfile, 'odpcourse')``

The load in turn will get the exact path to import the slide information from its parent as
there will be an internal get_odp_path for each entity. So we will know what to load into
the children entity. This is a particularity of the courseslide import.

This is the way we will be able to create the relevant item (quiz, file, discussion) from
any type of file.
For example if at some point we need to import an item from a gift.

    item.load('giftfile','gift')
    #OR
    item.gift.stream = 'giftfile'
    
or in a course:

    course[1][1].gift.stream = gift file

This will create the relevant quiz.

Basically the load function or the ``.<format>.stream`` property will create the relevant entity and attach
relevant entities to it. This is a fully recursive method that will create all child entities for examples:
 - File if this is a generic binary file (PDF)    
 - It can also create a dicussion or a quiz depending on what is in the input file

So the general process for odb:

``course.odpcourse.stream`` calls parse the odp file and get the basic information (slide 0) for the
course. It will in turn create a section per slide and then create items (depending on 
the item content and nature) for each bullet point in the slide. 

The creation of the item will be either direct via:
    bfile = ezdisteach.CourseModel('BinaryFile')
    bfile.title = "This is a pdf document"
    bfile.stream = <filepath> or stream # (will load the file for later use)
    bfile.name = 'filename.pdf'
    bfile.path = '' # Rooted in the item itsel


### Caching ?
Note that later we will need a cache system to avoid duplicating the opening / parsing of the ODP file

## Output

For output, we will have different choices from simple flat file to a folder like structure
like IMS Content packages, Moodle archive or edX archive.

The output process will be quite similar to the input.

``course.imscc.stream`` will return a streamed file which will contain both the metadata and the files from
its content.

course.imscc.meta will return a dictionary of metadata that can be iterated to create the relevant external
representation. We can go down in the hierarchy through the specialised <item>.items and <item>.parent accessor
for each item, so we can retrieve all meta information from the tree.

A filter can do this recursively the same way as the stream could do it. For example ``course.imscc.meta`` will return
the course manifest (imsmanifest.xml). 
A quiz located in the course would be output as ``quiz.imscc.meta``. Both will default to XML representation for metadata
output. In case we could have different types of representation we could use the sister method (similar to the pair
item.load() / item.stream) so to specify the representation to output.
The output of metadata will always be text like.  

We can format to xml by doing:
format(course.imscc.meta,'xml')

**Summary:**

We will have two main methods for exporting binary files: 
* ``course.imscc.stream`` => Streams a full IMSCC package (*.imscc)
* ``course.export('file', 'imscc')`` Will do the same

As per textual metadata:

* ``format(course.imscc,'xml')`` => Streams the full imsmanifest.xml
* ``course.imscc.meta`` : Streams the full imsmanifest.xml

Internally the course.imscc will output each children files in the relevant path and in  
a common folder. For each entity it will build up the lxml tree in to output in the 
 imsmanifest.xml.
 
For example for a course with several files and a quiz.

course.imscc.meta will build up xml representation ready to output in imsmanifest.xml. 
This will be done by going through each children and building up the xml representation for each. 
At this stage there is no way to encapsulate the generation of each item as :
* for xml representation - the child item will generate a fragment of XML that would then need to be parsed
again to be integration in the parent's XML representation. This would not be optimised
* for stream - a child item would then zip/pack its content so to be unpacked in the parent's container temporary
folder.

Best is then to have a recursive filter which would output metadata or stream representation where it make sense only.
For example for the IMSCC packaging:
* course.imscc.stream would output the full course ims package
* course.imscc.meta would output the content of the imsmanifest.xml file

So course.imscc.stream, would do:

* Create a temp folder
* Output self.imscc.meta into a file called imsmanifest.xml into the temporary folder
* For each course children, recursively check for children who have a working imscc.stream method, if so then
stream the content in a file and in a path that is defined by this item and its parent 
(for example a file with uid 909090 located in a quiz with uid 12345, would be streamed in i_12345/i_909090/<filename>)

The imscc.meta would do the same recursive routine with children and build an xml tree. If there is a working .imscc.meta
method for a given children, it would stream the content of this file using the same folder structure logic as per the
stream routine. 
It will get alongside the right <resource>, <file ref> and <item>

