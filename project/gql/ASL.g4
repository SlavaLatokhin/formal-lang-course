grammar ASL;

prog: stat* EOF;

stat: 'let' var '=' expr ';'
    | 'print' '(' expr ')' ';'
    ;

expr: '(' expr ')'
    | var
    | val
    | map
    | filter
    | intersection
    | concat
    | union
    | star
    ;

var:  LETTER_E (LETTER_E | '/' | '.' | '_' | DIGIT)*;

val:  '"' string '"'
    | '\'' char '\''
    | int
    | boolean
    | set
    | graph
    | vertices
    | edges
    | labels
    ;

string: (LETTER_E | '/' | '.' | '_' | ',' | ';' | ':' | DIGIT)* ;
char: LETTER_E;

int: ('-'? DIGIT+) | '0';
boolean: 'true' | 'false';
set: '{' val (',' val)* '}';

graph: var
    | 'set_start' '(' vertices ',' graph ')'
    | 'set_final' '(' vertices ',' graph ')'
    | 'add_start' '(' vertices ',' graph ')'
    | 'add_final' '(' vertices ',' graph ')'
    | 'load_graph' '(' '"'  string '"'  ')'
    | 'load_graph_from' '(' '"'  path '"'  ')'
    ;

path: string;

vertices:
    'get_start' '(' graph ')'
  | 'get_final' '(' graph ')'
  | 'get_vertices' '(' graph ')'
  | 'get_reachable' '(' graph ')'
  ;

edges: 'get_edges' '(' graph ')';

labels: 'get_labels' '(' graph ')';

map: 'map' '(' lambda ',' expr ')';
filter: 'filter' '(' lambda ',' expr ')';

lambda: 'fun' '(' var ')' '{' expr '}';

intersection: 'intersect' '(' expr ',' expr ')';

concat: 'concat' '(' expr ',' expr ')';

union: 'union' '(' expr ',' expr ')';

star: 'kleene' '(' expr ')';

DIGIT: [0-9];
LETTER_E: [a-zA-Z];
WS: ([ \t\n\r\f] | '/*' ~[\r\n]* '*/')+ -> skip;
