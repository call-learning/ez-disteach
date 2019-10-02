#Using ODP presentation to create a course

The aim is to create a full course model from a single presentation (in ODP format for now)

The base model is an item which stores internal information (structural info like title, description) 
and information on disk (mostly files).
What we need is to have a generic model that would account for most of the course structures (in Moodle, edX, IMS
Content packages).
For example 

|   ODP Document            |       EZ Disteach Internal Model   |
|---------------------------|------------------------------------|
|   Slideshow (first slide)               |      Course (title, description, language...)   |
|   Following slide from the slideshow   |      Course Section(title,description)   |
|   A bullet point (level 1) in a slide   |      Item(title, description)   | 


# Presentation and notes

The presentation will help to design the structure of a course and we will use extensively the "Notes" to develop
the content.
For example for the course information, the first slide will contain the Title and description of the course.
All other information will subsequently be stored in the note section.
We will use different types of languages to express the information at hand. For general configuration
it seems that TOML type of language is appropriate. Only downside is to be fault tolerant so we
don't prevent the full presentation from loading because of a space issue.

[TOML - Configuration language](https://fr.wikipedia.org/wiki/TOML)
[TOML - Specification](https://github.com/uiri/toml)

## First slide 

|   ODP First slide            |       EZ Disteach Internal Model   |
|---------------------------|------------------------------------|
|   Slide content               |      Course (title, description)   |
|   Slide Notes TOML content            | Course (language, keywords, other course settings...) |


For example:

|             |
|-------------|
|Slide 1 Title|
|Slide Description|
|-------------|

In the note section:
```
[meta] 
Tags = [ ‘Tag1’, ‘Tags2’, ‘Tag 3’] 
Langs = [‘fr’, ‘en’]
```

## Subsequent slides

Each slide will have a bullet point list which states the course structure. Each bullet point
will describe in a sort of natural language (like gherkin for test scenario)
For now it is just a simple parser which will just state the type of ressource and its name.
The name will then be used to search in the note section for more information.

Examples:

* Un label "Mon Label"
* Un lien vers "http://www.wikipedia.org"
* Un lien nommé "Wikipedia" vers "http://www.wikipedia.org"
* Une vidéo externe nommée "Vidéo d'exemple" vers "https://www.youtube.com/watch?v=aqz-KE-bpKQhttps://www.youtube.com/watch?v=aqz-KE-bpKQ"
* Une vidéo interne nommée "Vidéo interne" du fichier "VIDEO-1.1.mp4"
* Un quiz nommé "Quiz 1"
* Un quiz nommé "Quiz 1" du fichier "quiz.docx"
* Une image nommée "Image" de "NOM DE L'IMAGE DANS LE SLIDE" 

Donc on aurait un language basique qui permettrait d'exprimer avec TYPE_DE_RESSOURCE étant label,
video externe, video interne, quiz, lien.
* TYPE_DE_RESSOURCE nommé(e) "NOM_AFFICHABLE"
* TYPE_DE_RESSOURCE nommé(e) "NOM_AFFICHABLE" vers "URL"
* TYPE_DE_RESSOURCE nommé(e) "NOM_AFFICHABLE" du fichier "NOM_FICHIER_ARCHIVE"

Dans les notes on aura des section réservées pour chaque ressource nommée, à la manière de TOML
\[NOM_DE_LA_RESSOURCE\] qui comprendront les paramétrages pour cette ressource.

Par exemple pour un quiz:
[Quiz 1]
type = "aiken"

What is the correct answer to this question?
A. Is it this one?
B. Maybe this answer?
C. Possibly this one?
D. Must be this one!
ANSWER: D

[Quiz 2]
type = "gift"

// true/false
::Q1:: 1+1=2 {T}

// Choix multiple avec rétroaction spécifique pour les bonnes et les mauvaises réponses
::Q2:: Quelle couleur se trouve entre l'orange et le vert dans le spectre ? 
{=jaune #Bonne réponse; bravo ! ~rouge #Mauvaise réponse, c'est jaune. ~bleu #Mauvaise réponse, c'est jaune.}

// Texte troué
::Q3:: Deux plus {=deux =2} égalent quatre.











    

