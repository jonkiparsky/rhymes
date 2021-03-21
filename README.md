# rhymes
Code about rhymes

Some useful resources:

Basis for syllabizing words is the CMU pronouncing Dictionary
https://en.wikipedia.org/wiki/CMU_Pronouncing_Dictionary
"Official version" (cited by cmu) is the svn repo:
http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/
Also at github: https://github.com/cmusphinx/cmudict (this might be better
maintained, but the format has changed a bit, so the code below would need
to be tweaked)
Can also import this data via nltk, but installing nltk is annoying and
maybe not super helpful.
Note: github and nltk versions use lowercase entries and uppercase syllables,
svn uses uppercase for both. Arbitrarily normalizing to lowercase here.

CMU dict uses an enriched form of ARPAbet:
see https://en.wikipedia.org/wiki/ARPABET

CMU uses the 2-letter variant, with stress indicators. Stress is indicated by
digits appended to vowels, and is a little confusing: 1 is primary stress,
2 is secondary stress, and 0 is no stress. (so 1 > 2 > 0).
`humanize_stress` converts to a a sensible format



Readings:
Zwicky, Linguistics and Folk Poetry

To do:
- html output generation fails due to titles, etc, preceding poem

