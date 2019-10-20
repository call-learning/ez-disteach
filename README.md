# Introduction

This project aims to easily convert a document input (mainly Presentations, as ODP documents) into
a variety of outputs (IMS Content Package, Moodle archive or edX course).
The ODP document will contain the course structure and have some information about quiz and so on.

In order to do that we have defined a base model to store internal information (structural info like title, description) 
and information on disk (mostly files).

For example: 

|   ODP Document            |       EZ Disteach Internal Model   |          IMS Content Package                 |
|---------------------------|------------------------------------|----------------------------------------------|
|   Slideshow               |      Course (title, description, language...)   |    The whole package metadata   |
|   A slide from the slideshow   |      Course Section(title,description)   |    An item (metadata) without IdentifierRef   |
|   A bullet point (level 1) in a slide   |      Item(title, description, content)   |    An item (metadata) with IdentifierRef and ressources attached   |


# Notes

This project is still at an early stage and not ready for production.
