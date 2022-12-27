import pytest

from project.gql.parser import save_parse_tree_as_dot


@pytest.mark.parametrize(
    "text, result",
    [
        (
            "let a = 5 /*some comments*/;",
            """strict digraph parse_tree {
0 [label=prog];
1 [label=stat];
0 -> 1;
2 [label="'let'"];
1 -> 2;
3 [label=var];
1 -> 3;
4 [label="'a'"];
3 -> 4;
5 [label="'='"];
1 -> 5;
6 [label=expr];
1 -> 6;
7 [label=val];
6 -> 7;
8 [label=int];
7 -> 8;
9 [label="'5'"];
8 -> 9;
10 [label="';'"];
1 -> 10;
11 [label="'<EOF>'"];
0 -> 11;
}""",
        ),
        (
            "print(set_start(get_vertices(graph), graph)); /* получение вершин графа и назначение их стартовыми */",
            """strict digraph parse_tree {
0 [label=prog];
1 [label=stat];
0 -> 1;
2 [label="'print'"];
1 -> 2;
3 [label="'('"];
1 -> 3;
4 [label=expr];
1 -> 4;
5 [label=val];
4 -> 5;
6 [label=graph];
5 -> 6;
7 [label="'set_start'"];
6 -> 7;
8 [label="'('"];
6 -> 8;
9 [label=vertices];
6 -> 9;
10 [label="'get_vertices'"];
9 -> 10;
11 [label="'('"];
9 -> 11;
12 [label=graph];
9 -> 12;
13 [label=var];
12 -> 13;
14 [label="'g'"];
13 -> 14;
15 [label="'r'"];
13 -> 15;
16 [label="'a'"];
13 -> 16;
17 [label="'p'"];
13 -> 17;
18 [label="'h'"];
13 -> 18;
19 [label="')'"];
9 -> 19;
20 [label="','"];
6 -> 20;
21 [label=graph];
6 -> 21;
22 [label=var];
21 -> 22;
23 [label="'g'"];
22 -> 23;
24 [label="'r'"];
22 -> 24;
25 [label="'a'"];
22 -> 25;
26 [label="'p'"];
22 -> 26;
27 [label="'h'"];
22 -> 27;
28 [label="')'"];
6 -> 28;
29 [label="')'"];
1 -> 29;
30 [label="';'"];
1 -> 30;
31 [label="'<EOF>'"];
0 -> 31;
}""",
        ),
    ],
)
def test_write_dot(tmpdir, text, result):
    file = tmpdir.mkdir("test_dir").join("cfg_file")
    save_parse_tree_as_dot(text, file)
    print(file.read())
    assert file.read().strip() == result
