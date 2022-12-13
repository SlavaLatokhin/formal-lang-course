# Язык запросов к графам

## Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Char of char
  | Int of int
  | Bool of bool
  | Set_val of set<val>
  | Graph of graph
  | Labels of labels
  | Vertices of vertices
  | Edges of edges

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda =
    // а здесь пространство для творчества
```

## Конкретный синтаксис

```
<prog> --> <stmt>*

<stmt> --> let <var> = <expr>; | "print" (<expr>);

<expr> -->
    (<expr>)
  | <var>
  | <val>
  | <map>
  | <filter>
  | <intersection>
  | <concat>
  | <union>
  | <star>

<var> --> <initial> <subsequent>*
<initial> --> <letter> | <special>
<letter> --> <lowercase> | <uppercase>
<lowercase> --> a | b | c | ... | z
<uppercase> --> A | B | C | ... | Z
<subsequent> --> <initial> | <digit> | <special>
<non zero digit> --> 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<digit> --> 0 | <non zero digit>
<special> --> _ | /

<val> -->
    "<string>"
  | '<char>'
  | <boolean>
  | <int>
  | <set>
  | <graph>
  | <vertices>
  | <edges>
  | <labels>

<string> --> <subsequent>*
<char> --> <letter>
<boolean> --> true | false
<int> --> <non zero digit> <digit>*
<set> --> {<val>*}

<graph> -->
    set_start (<set>, <graph>)
  | set_final (<set>, <graph>)
  | add_start (<set>, <graph>)
  | add_final (<set>, <graph>)
  | load_graph (<string>)
  | load_graph_from (<path>)

<path> -> <string>

<vertices> -->
    get_start (<graph>)
  | get_final (<graph>)
  | get_vertices (<graph>)
  | get_reachable (<graph>)

<edges> --> get_edges (<graph>)

<labels> --> get_labels (<graph>)

<map> --> map (<lambda>, <expr>)
<filter> --> filter (<lambda>, <expr>)

<lambda> --> fun (<var>) {<expr>}

<intersection> --> <expr> && <expr> | intersect(<expr>, <expr>)

<concat> --> <expr> ~~ <expr> | concat(<expr>, <expr>)

<union> --> <expr> || <expr> | union(<expr>, <expr>)

<star> --> (<expr>)** | kleene(<expr>)
```

## Пример программы

```
let graph = load_graph("atom"); // загрузка графа по названию
let graph = load_graph_from("data/wine.dot"); // загрузка графа их файла

let graph = set_start(get_vertices(graph)[0], graph); // получение одной из вершин графа и назначение ее стартовой
let graph = set_final(get_start(graph), graph); // получение стартовых вершин графа и назначение их финальными

let x = ("label1" || "label2"); // создание запроса

let intersection = graph && x; // набор вершин, удовлетворяющих запросу

print(intersection); // печать переменной

```

## Правила вывода типов

Константы типизируются очевидным образом.

Тип переменной определяется типом выражения, с которым она связана.
```
[b(v)] => t
_________________
[Var (v)](b) => t
```

Загрузить можно только автомат.
```
_________________________
[Load (p)](b) => FA<int>
```

Установка финальных состояний, а так же добавление стартовых и финальных типизируется аналогично типизации установки стартовых, которая приведена ниже.
```
[s](b) => Set<t> ;  [e](b) => FA<t>
___________________________________
[Set_start (s, e)](b) => FA<t>


[s](b) => Set<t> ;  [e](b) => RSM<t>
____________________________________
[Set_start (s, e)](b) => RSM<t>

```

Получение финальных типизируется аналогично получению стартовых, правила для которого приведены ниже.
```
[e](b) => FA<t>
____________________________
[Get_start (e)](b) => Set<t>


[e](b) => RSM<t>
____________________________
[Get_start (e)](b) => RSM<t>

```

```
[e](b) => FA<t>
__________________________________
[Get_reachable (e)](b) => Set<t*t>


[e](b) => RSM<t>
__________________________________
[Get_reachable (e)](b) => Set<t*t>

```

```
[e](b) => FA<t>
_______________________________
[Get_vertices (e)](b) => Set<t>


[e](b) => RSM<t>
_______________________________
[Get_vertices (e)](b) => Set<t>


[e](b) => FA<t>
______________________________________
[Get_edges (e)](b) => Set<t*string*t>


[e](b) => RSM<t>
______________________________________
[Get_edges (e)](b) => Set<t*string*t>

[e](b) => FA<t>
__________________________________
[Get_labels (e)](b) => Set<string>


[e](b) => RSM<t>
__________________________________
[Get_labels (e)](b) => Set<string>

```

Правила для ```map``` и ```filter``` традиционные.
```
[f](b) => t1 -> t2 ; [q](b) => Set<t1>
_______________________________________
[Map (f,q)](b) => Set<t2>


[f](b) => t1 -> bool ; [q](b) => Set<t1>
________________________________________
[Filter (f,q)](b) => Set<t1>
```

Пересечение для двух КС не определено.
```
[e1](b) => FA<t1> ;  [e2](b) => FA<t2>
______________________________________
[Intersect (e1, e2)](b) => FA<t1*t2>


[e1](b) => FA<t1> ;  [e2](b) => RSM<t2>
_______________________________________
[Intersect (e1, e2)](b) => RSM<t1*t2>


[e1](b) => RSM<t1> ;  [e2](b) => FA<t2>
_______________________________________
[Intersect (e1, e2)](b) => RSM<t1*t2>

```

Остальные операции над автоматами типизируются согласно формальных свойств классов языков.
```
[e1](b) => FA<t> ;  [e2](b) => FA<t>
_____________________________________
[Concat (e1, e2)](b) => FA<t>


[e1](b) => FA<t> ;  [e2](b) => RSM<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => FA<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => RSM<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>

```

```
[e1](b) => FA<t> ;  [e2](b) => FA<t>
______________________________________
[Union (e1, e2)](b) => FA<t>


[e1](b) => FA<t> ;  [e2](b) => RSM<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => FA<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>


[e1](b) => RSM<t> ;  [e2](b) => RSM<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>

```

```
[e](b) => FA<t>
______________________
[Star (e)](b) => FA<t>


[e](b) => RSM<t>
______________________
[Star (e](b) => RSM<t>

```

```
[e](b) => string
________________________
[Smb (e)](b) => FA<int>

```

## Динамическая семантика языка запросов

Связывание переопределяет имя.

```
[e](b1) => x,b2
_____________________________________
[Bind (v, e)](b1) => (), (b1(v) <= x)

```

Загрузить можно только автомат и у него все вершины будут стартовыми и финальными.

```
[p](b1) => s,b2 ; read_fa_from_file s => fa
_____________________________________
[Load (p)](b1) => (fa | fa.start = fa.vertices, fa.final = fa.vertices), b1

```
