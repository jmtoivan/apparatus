#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Graphical user interface for using the poetry generator.

.. module:: gui
"""

from Tkinter import *
import generate_multilingual

class App:

    def __init__(self, master):

        bgcolour = 'LightSkyBlue2' #'gray90'
        selectioncolour = 'LightSkyBlue3' #'gray87'
        master.title("P.O. Eticus-Apparatus")

        languages = [('English', 'en'), ('French', 'fr'), ('Finnish', 'fi')]

        en_corpora = [('English Poems', './poetry/english_poems.txt'),
                      ('Imagist Poetry', './poetry/imagist_poetry.txt')]
        fr_corpora = [(u'Poesie française', './poesie/poesie_francaise.txt')]
        fi_corpora = []

        en_graphs = [('LLR', './graphs/small_graph.db'),
                     ('LSA', './graphs/lsa.db')]
        fr_graphs = [('LLR', './graphs/french_pruned.db')]
        fi_graphs = []

        def show_corpora(corpora):
            self.corpus_box.delete(0, END)
            for text, corpus in corpora:
                self.corpus_box.insert(END, text)
            self.corpora = corpora
            self.corpus_box.selection_set(first=0)

        def show_graphs(graphs):
            self.graph_box.delete(0, END)
            for text, graph in graphs:
                self.graph_box.insert(END, text)
            self.graphs = graphs
            self.graph_box.selection_set(first=0)
            
        def choose_language():
            selection = var.get()
            if selection == 'en':
                show_corpora(en_corpora)
                show_graphs(en_graphs)
            if selection == 'fr':
                show_corpora(fr_corpora)
                show_graphs(fr_graphs)
            if selection == 'fi':
                show_corpora(fi_corpora)
                show_graphs(fi_graphs)
            self.theme_entry.delete(0, END)
            
        def write_poem():
            # Delete the results of the previous poem generation
            self.new_poem.delete(1.0, END)
            self.orig_poem.delete(1.0, END)
            self.new_words.delete(1.0, END)

            # Get the selected language
            language = var.get()
            
            # Get the selected corpus
            j = self.corpus_box.curselection()
            input_corpus = self.corpora[int(j[0])]
            

            # Get the selected graph
            i = self.graph_box.curselection()
            input_db = self.graphs[int(i[0])]

            # Get the given theme
            input_theme = self.theme_entry.get()

            # Generate the poem
            (new_theme,
             orig,
             new,
             replacing_words,
             message) = generate_multilingual.generate(language,
                                                       input_corpus[1],
                                                       input_db[1],
                                                       theme=input_theme)


            # Show the results
            if not input_theme:
                self.theme_entry.insert(0, new_theme)
            self.orig_poem.insert(END, orig)
            self.new_poem.insert(END, new)
            for word in replacing_words:
                self.new_words.insert(END, word[0] + ' ' + word[1] + '\n')

            print('Corpus: ' + input_corpus[1])
            print('Graph: ' + input_db[1])
            print('Theme: ' + new_theme)
            print('Original poem: ')
            print(orig)
            print('New poem: ')
            print(new)
            print(message)

        def write_poem_a(event):
            write_poem()

        # Main frame
        frame = Frame(master, background=bgcolour, borderwidth=20)
        frame.pack()

        # Pressing the enter key generates a poem. 
        root.bind('<Return>', write_poem_a)
        
        # Language selection radiobuttons
        self.button_frame = Frame(frame, background=bgcolour)
        var = StringVar(self.button_frame)
        var.set(languages[0][1])
        for text, value in languages:
            self.button = Radiobutton(self.button_frame,
                                      background=bgcolour,
                                      highlightthickness=0,
                                      text=text,
                                      variable=var,
                                      value=value,
                                      command=choose_language)
            self.button.pack(anchor=W)
        self.button_frame.grid(row=1, column=0, sticky=W)

        # "Select the corpus" label
        self.select_corpus = Label(frame, background=bgcolour,
                                   text="Select corpus:")
        self.select_corpus.grid(row=0, column=1)

        # Corpus selection listbox
        self.corpus_box = Listbox(frame,
                                  exportselection=0,
                                  selectbackground=selectioncolour,
                                  selectmode='browse',
                                  width=15, height=5)
        show_corpora(en_corpora)
        self.corpus_box.grid(row=1, column=1, rowspan=2, sticky=N)

        # "Select the graph" label
        self.select_graph = Label(frame, background=bgcolour,
                                  text="Select graph:")
        self.select_graph.grid(row=0, column=2)

        # Graph selection listbox
        self.graph_box = Listbox(frame,
                                 exportselection=0,
                                 selectbackground=selectioncolour,
                                 selectmode='browse',
                                 width=15, height=5)
        show_graphs(en_graphs)
        self.graph_box.grid(row=1, column=2, rowspan=2, sticky=N)

        # Theme label
        self.theme_label = Label(frame, background=bgcolour,
                                 text = 'Theme (optional):')
        self.theme_label.grid(row=0, column=3)

        # Theme entry
        self.theme_entry = Entry(frame, width=15)
        self.theme_entry.grid(row=1, column=3, sticky=N)

        # "Generate poem" button
        self.poetry_button = Button(frame,
                                    background=selectioncolour,
                                    text="Generate poem",
                                    command=write_poem,
                                    width=13)
        self.poetry_button.grid(row=2, column=3, sticky=N)

        # New poem text
        self.new_poem_frame = Frame(frame, background=bgcolour)
        self.new_poem_label = Label(self.new_poem_frame, background=bgcolour,
                                    text = 'New poem:')
        self.new_poem_label.pack(side=TOP)
        self.yscroll=Scrollbar(self.new_poem_frame, background=bgcolour)
        self.yscroll.pack(side=RIGHT, fill=Y)
        self.new_poem = Text(self.new_poem_frame,
                        height=15, width=60,
                        wrap=WORD,
                        yscrollcommand=self.yscroll.set)
        self.new_poem.pack(side=LEFT)
        self.yscroll.config(command=self.new_poem.yview)
        self.new_poem_frame.grid(row=3, columnspan=3)

        # Original poem text
        self.orig_poem_frame = Frame(frame, background=bgcolour)
        self.orig_poem_label = Label(self.orig_poem_frame,
                                     background=bgcolour,
                                     text = 'Original poem:')
        self.orig_poem_label.pack(side=TOP)
        self.yscroll2=Scrollbar(self.orig_poem_frame, background=bgcolour)
        self.yscroll2.pack(side=RIGHT, fill=Y)
        self.orig_poem = Text(self.orig_poem_frame,
                         height=15, width=60,
                         wrap=WORD,
                         yscrollcommand=self.yscroll2.set)
        self.orig_poem.pack(side=LEFT)        
        self.yscroll2.config(command=self.orig_poem.yview)
        self.orig_poem_frame.grid(row=4, columnspan=3)

        # New words text
        self.words_frame = Frame(frame, background=bgcolour)
        self.words_label = Label(self.words_frame, background=bgcolour,
                                 text = 'New words:')
        self.words_label.pack(side=TOP)
        self.yscroll3=Scrollbar(self.words_frame, background=bgcolour)
        self.yscroll3.pack(side=RIGHT, fill=Y)
        self.new_words = Text(self.words_frame, height=33, width=20,
                         yscrollcommand=self.yscroll3.set)
        self.new_words.pack(side=LEFT)        
        self.yscroll3.config(command=self.new_words.yview)
        self.words_frame.grid(row=3, rowspan=2, column=3)

        master.mainloop()

root = Tk()

app = App(root)

root.mainloop()
    
