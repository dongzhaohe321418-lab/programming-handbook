# Concept index

This is the back-of-the-book index: an alphabetical list of the concepts the
handbook teaches, each pointing at the section that actually teaches it. It is
deliberately *not* a glossary — [Appendix C](appendix/C-glossary.md) and
[Appendix E](appendix/E-ai-glossary.md) define terms, while this page only
locates them, so when a term has a glossary entry you will often see both links
here: the chapter for the lesson, the appendix for the one-paragraph reminder.

Entries list one to three places, most useful first. Where an idea is taught
twice at different depths, both are given and labelled ("first look", "in
depth"), so you can choose the introduction or the implementation.

## A

abstract base class (ABC)
:   [15.3 Interfaces and abstract classes](ch15-inheritance/03-interfaces.md) — see also **interface**, **duck typing**

abstract data type (ADT)
:   [18.1 Abstract data types and generics](ch18-linked-lists/01-adts-generics.md) · [Appendix C](appendix/C-glossary.md#a)

access modifier
:   [13.1 Encapsulation and access control](ch13-design/01-encapsulation.md) · Java syntax in [Appendix A · Python ↔ Java cheat sheet](appendix/A-python-java.md)

address space and memory segments
:   [23.2 The memory layout of a program](ch23-os/02-memory-layout.md) · the two-region picture first in [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md)

adjacency list
:   [37.1 Representing graphs](ch37-graphs/01-representations.md)

adjacency matrix
:   [37.1 Representing graphs](ch37-graphs/01-representations.md)

admissible heuristic
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md) — see also **A\* search**

advantage
:   [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md) · group-relative form in [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md) · [Appendix E](appendix/E-ai-glossary.md#a)

agent
:   [30.1 The agent loop and ReAct](ch30-agents/01-agent-loop-react.md) · [Appendix E](appendix/E-ai-glossary.md#a)

agent loop
:   [30.1 The agent loop and ReAct](ch30-agents/01-agent-loop-react.md) · built from scratch in [Project 6 · A ReAct Agent from Scratch](projects/06-react-agent/README.md)

aliasing
:   [9.1 Values vs references](ch09-collections/01-references.md) — in depth · first met in [4.3 Equality vs identity](ch04-branching/03-equality-identity.md)

amortized cost
:   [16.3 The complexity zoo](ch16-complexity/03-complexity-zoo.md) — in depth · first met with `append` in [9.2 Dynamic lists — ArrayList and list](ch09-collections/02-dynamic-lists.md)

anchor (regex)
:   [41.1 Regex fundamentals](ch41-regex/01-fundamentals.md)

ANN index (approximate nearest neighbour)
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md) · [Appendix E](appendix/E-ai-glossary.md#a)

argument
:   [3.3 Writing your own functions](ch03-functions/03-writing-functions.md) — see also **keyword argument**, **parameter**

arrange–act–assert
:   [24.2 Testing beyond the basics](ch24-practice/02-testing.md)

array
:   [7.1 Arrays vs Python lists](ch07-arrays/01-arrays-vs-lists.md) · two-dimensional in [8.1 Two-dimensional arrays](ch08-grids/01-2d-arrays.md) · [Appendix C](appendix/C-glossary.md#a)

`ArrayList`
:   [9.2 Dynamic lists — ArrayList and list](ch09-collections/02-dynamic-lists.md)

ASCII
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) — see also **Unicode**

A\* search
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md) · applied in [Project 9 · Route Finder (Graphs)](projects/09-route-finder/README.md)

`assert` statement
:   [8.4 Unit testing](ch08-grids/04-unit-testing.md) · framework assertions in [40.4 JUnit and testing at scale](ch40-toolchain/04-junit.md)

attention
:   [26.2 Embeddings and attention](ch26-llm-internals/02-attention.md) · [Appendix E](appendix/E-ai-glossary.md#a)

autocomplete
:   [36.3 Tries](ch36-hashing-tries/03-tries.md)

AVL tree
:   [35.2 AVL trees](ch35-balanced-trees/02-avl.md) · rotations first in [35.1 Rotations](ch35-balanced-trees/01-rotations.md)

AWQ
:   [27.4 Quantization and deployment](ch27-inference/04-quantization-deploy.md) · [Appendix E](appendix/E-ai-glossary.md#g)

## B

backpressure
:   [39.3 Generators, pipelines, and Unix pipes](ch39-streams/03-pipelines.md) · in a streaming server in [27.3 Latency, throughput, and streaming](ch27-inference/03-latency-streaming.md)

backreference (regex)
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md)

backtracking, catastrophic
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md) — see also **ReDoS**

balance factor
:   [35.2 AVL trees](ch35-balanced-trees/02-avl.md)

bandit problem
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

base case
:   [17.1 The call stack](ch17-recursion/01-call-stack.md) · worked examples in [17.2 Classic recursive problems](ch17-recursion/02-classic-recursion.md) · [Appendix C](appendix/C-glossary.md#b)

baseline (variance reduction)
:   [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md) — in depth · introduced in [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

bash
:   [40.1 Bash scripting](ch40-toolchain/01-bash.md) · syntax card in [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

batching
:   [27.2 Batching, PagedAttention, chunked prefill](ch27-inference/02-batching.md) · [Appendix E](appendix/E-ai-glossary.md#b)

Bellman–Ford algorithm
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md)

benchmark
:   [33.1 Benchmarks and what they measure](ch33-eval/01-benchmarks.md) · [Appendix E](appendix/E-ai-glossary.md#b)

best, worst, and average case
:   [16.1 Big-O notation](ch16-complexity/01-big-o.md) · [Appendix B · Big-O reference](appendix/B-big-o.md)

Big-O notation
:   [16.1 Big-O notation](ch16-complexity/01-big-o.md) · reference tables in [Appendix B · Big-O reference](appendix/B-big-o.md) · [Appendix C](appendix/C-glossary.md#b)

binary (base 2)
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) · conversions in [2.2 Number systems](ch02-data/02-number-systems.md) · built as a tool in [Project 1 · Number-Systems Toolkit](projects/01-number-tool/README.md)

binary search
:   [22.3 Searching](ch22-sorting/03-searching.md) — in depth · recursive version in [17.2 Classic recursive problems](ch17-recursion/02-classic-recursion.md)

binary search tree (BST)
:   [20.2 BST operations](ch20-bst/02-bst-ops.md) · vocabulary first in [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md) · [Appendix C](appendix/C-glossary.md#b)

bipartite graph
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md)

bit
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) · [Appendix C](appendix/C-glossary.md#b)

bitwise operators
:   [6.4 Bitwise operators and enums](ch06-loops/04-bitwise-enums.md)

black-height
:   [35.3 Red-black trees](ch35-balanced-trees/03-red-black.md)

Boolean
:   [4.1 Booleans and logic](ch04-branching/01-booleans-logic.md) · [Appendix C](appendix/C-glossary.md#b)

bootstrap confidence interval
:   [33.2 Building an eval harness](ch33-eval/02-eval-harness.md) · applied in [Project 8 · An Evaluation Harness](projects/08-eval-harness/README.md)

box model (CSS)
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md)

BPE (byte-pair encoding)
:   [26.1 From text to tokens](ch26-llm-internals/01-tokenization.md) · [Appendix E](appendix/E-ai-glossary.md#b)

Bradley–Terry model
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md) · [Appendix E](appendix/E-ai-glossary.md#b)

branch (Git)
:   [24.1 A real Git workflow](ch24-practice/01-git-workflow.md) — in depth · first taste in [1.3 Git and version control, first taste](ch01-tools/03-git.md)

branching factor
:   [35.4 B-trees and the disk](ch35-balanced-trees/04-b-trees.md)

breadth-first search (BFS)
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md) · the same shape as level-order traversal in [20.3 Traversals and the balance problem](ch20-bst/03-traversals-balance.md)

`break`
:   [6.3 Nested loops, break, continue](ch06-loops/03-nested-break-continue.md)

B-tree and B+ tree
:   [35.4 B-trees and the disk](ch35-balanced-trees/04-b-trees.md)

bucket (hash table)
:   [36.1 Hash tables from scratch](ch36-hashing-tries/01-hash-tables.md)

bucket sort
:   [38.2 Counting, radix, and bucket sort](ch38-linear-sorting/02-counting-radix-bucket.md)

byte
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md)

bytecode
:   [0.3 What is a program — compilers and interpreters](ch00-machine/03-programs.md) — first look · the CPython pipeline in [23.3 Interpreters and virtual machines](ch23-os/03-interpreters-vms.md)

## C

call stack
:   [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md) — first look · traced through recursion in [17.1 The call stack](ch17-recursion/01-call-stack.md) · [Appendix C](appendix/C-glossary.md#c)

capturing group
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md)

causal mask
:   [26.2 Embeddings and attention](ch26-llm-internals/02-attention.md)

chaining (hash collisions)
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

character class (regex)
:   [41.1 Regex fundamentals](ch41-regex/01-fundamentals.md)

chunked prefill
:   [27.2 Batching, PagedAttention, chunked prefill](ch27-inference/02-batching.md)

chunking (for retrieval)
:   [29.2 The RAG pipeline](ch29-memory-rag/02-rag-pipeline.md) · [Appendix E](appendix/E-ai-glossary.md#c)

circular buffer
:   [19.3 Queues](ch19-stacks-queues/03-queues.md)

class
:   [12.1 Anatomy of a class](ch12-classes/01-class-anatomy.md) · worked builds in [12.2 Worked examples — Dog, WeatherStation](ch12-classes/02-worked-examples.md) · [Appendix C](appendix/C-glossary.md#c)

class attribute vs instance attribute
:   [12.1 Anatomy of a class](ch12-classes/01-class-anatomy.md)

clipped objective (PPO)
:   [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md)

closure
:   [39.1 Lambdas and higher-order functions](ch39-streams/01-lambdas.md) — see also **late binding**

code review
:   [24.3 Style, reviews, and readable code](ch24-practice/03-style-review.md) — in depth · the practice around a pull request in [24.1 A real Git workflow](ch24-practice/01-git-workflow.md)

Cohen's kappa
:   [33.3 LLM-as-a-judge](ch33-eval/03-llm-as-judge.md)

collision (hash)
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md) · [Appendix C](appendix/C-glossary.md#c)

command line
:   [1.1 The command line](ch01-tools/01-command-line.md) · writing programs for it in [10.1 Command-line programs and arguments](ch10-exceptions/01-cli-programs.md) · [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

commit (Git)
:   [1.3 Git and version control, first taste](ch01-tools/03-git.md) · commit messages in [24.1 A real Git workflow](ch24-practice/01-git-workflow.md)

comparison lower bound
:   [38.1 The comparison lower bound](ch38-linear-sorting/01-lower-bound.md)

compiler
:   [0.3 What is a program — compilers and interpreters](ch00-machine/03-programs.md) · [Appendix C](appendix/C-glossary.md#c)

composition
:   [12.2 Worked examples — Dog, WeatherStation](ch12-classes/02-worked-examples.md) · as a UML relationship in [13.2 UML class diagrams](ch13-design/02-uml.md)

comprehension (list, dict, set)
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md)

connected component
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md)

constrained decoding
:   [28.2 Structured output and constrained decoding](ch28-tools-mcp/02-structured-output.md) · [Appendix E](appendix/E-ai-glossary.md#c)

constructor
:   [12.1 Anatomy of a class](ch12-classes/01-class-anatomy.md) · chaining with `super()` in [15.1 Inheritance](ch15-inheritance/01-inheritance.md)

contamination
:   [32.1 Why data decides everything](ch32-data/01-why-data.md) — in the corpus · what it does to scores in [33.1 Benchmarks and what they measure](ch33-eval/01-benchmarks.md)

context window
:   [29.3 Agent memory and context management](ch29-memory-rag/03-agent-memory.md) — as a budget · measured in tokens in [26.1 From text to tokens](ch26-llm-internals/01-tokenization.md) · [Appendix E](appendix/E-ai-glossary.md#c)

`continue`
:   [6.3 Nested loops, break, continue](ch06-loops/03-nested-break-continue.md)

continuous batching
:   [27.2 Batching, PagedAttention, chunked prefill](ch27-inference/02-batching.md) · [Appendix E](appendix/E-ai-glossary.md#c)

cookie
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

copy, shallow vs deep
:   [9.1 Values vs references](ch09-collections/01-references.md)

cosine similarity
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md) · [Appendix E](appendix/E-ai-glossary.md#c)

`Counter`
:   [14.1 Sets, maps, and dictionaries](ch14-beyond/01-collections-tour.md)

counting sort
:   [38.2 Counting, radix, and bucket sort](ch38-linear-sorting/02-counting-radix-bucket.md)

coverage (test)
:   [24.2 Testing beyond the basics](ch24-practice/02-testing.md)

CPU
:   [0.1 What is a computer, really](ch00-machine/01-hardware.md) · [Appendix C](appendix/C-glossary.md#c)

credit assignment
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md)

CSS
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md)

cut property
:   [37.4 Minimum spanning trees](ch37-graphs/04-mst.md)

cycle detection
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md) · in a build graph in [40.3 Make and build systems](ch40-toolchain/03-make.md)

## D

DAG (directed acyclic graph)
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md) — see also **topological sort**

data binding
:   [42.4 Desktop GUIs — JavaFX and tkinter](ch42-web-gui/04-desktop-gui.md)

decision tree (sorting)
:   [38.1 The comparison lower bound](ch38-linear-sorting/01-lower-bound.md)

decontamination
:   [32.4 Filtering, dedup, and verification](ch32-data/04-filtering.md)

deduplication
:   [32.4 Filtering, dedup, and verification](ch32-data/04-filtering.md) · [Appendix E](appendix/E-ai-glossary.md#d)

degree (of a vertex)
:   [37.1 Representing graphs](ch37-graphs/01-representations.md)

depth (of a node)
:   [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md) — see also **height (of a tree)**

depth-first search (DFS)
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md)

`deque`
:   [19.3 Queues](ch19-stacks-queues/03-queues.md) · why it is a doubly linked list in [18.3 Doubly linked lists](ch18-linked-lists/03-doubly-linked.md)

dictionary
:   [14.1 Sets, maps, and dictionaries](ch14-beyond/01-collections-tour.md) — how to use one · [36.1 Hash tables from scratch](ch36-hashing-tries/01-hash-tables.md) — how one works · [Appendix C](appendix/C-glossary.md#d)

Dijkstra's algorithm
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md) · applied in [Project 9 · Route Finder (Graphs)](projects/09-route-finder/README.md)

directed vs undirected graph
:   [37.1 Representing graphs](ch37-graphs/01-representations.md)

dispatch, dynamic
:   [15.2 Polymorphism and casting](ch15-inheritance/02-polymorphism.md) · [Appendix C](appendix/C-glossary.md#d)

distillation
:   [32.2 Synthetic data generation](ch32-data/02-synthetic-data.md) · [Appendix E](appendix/E-ai-glossary.md#d)

DOM (document object model)
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md) — the tree · scripting it in [42.3 JavaScript in the browser](ch42-web-gui/03-javascript.md)

dominant term
:   [16.1 Big-O notation](ch16-complexity/01-big-o.md)

doubly linked list
:   [18.3 Doubly linked lists](ch18-linked-lists/03-doubly-linked.md)

DPO (Direct Preference Optimization)
:   [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md) · built end to end in [Project 7 · Preference Alignment with DPO](projects/07-dpo-alignment/README.md) · [Appendix E](appendix/E-ai-glossary.md#d)

duck typing
:   [15.2 Polymorphism and casting](ch15-inheritance/02-polymorphism.md) · weighed against ABCs in [15.3 Interfaces and abstract classes](ch15-inheritance/03-interfaces.md)

dynamic typing
:   [2.1 Variables and types](ch02-data/01-variables-types.md) · [Python and Java](python-vs-java.md)

## E

edge (graph)
:   [37.1 Representing graphs](ch37-graphs/01-representations.md)

embedding
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md) — for retrieval · inside a transformer in [26.2 Embeddings and attention](ch26-llm-internals/02-attention.md) · [Appendix E](appendix/E-ai-glossary.md#e)

encapsulation
:   [13.1 Encapsulation and access control](ch13-design/01-encapsulation.md) · [Appendix C](appendix/C-glossary.md#e)

enum
:   [6.4 Bitwise operators and enums](ch06-loops/04-bitwise-enums.md)

epsilon-greedy
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md) · [Appendix E](appendix/E-ai-glossary.md#e)

equality (`==`) vs identity (`is`)
:   [4.3 Equality vs identity](ch04-branching/03-equality-identity.md) · why it matters for collections in [9.1 Values vs references](ch09-collections/01-references.md)

eval harness
:   [33.2 Building an eval harness](ch33-eval/02-eval-harness.md) · built in [Project 8 · An Evaluation Harness](projects/08-eval-harness/README.md) · [Appendix E](appendix/E-ai-glossary.md#e)

event loop
:   [42.3 JavaScript in the browser](ch42-web-gui/03-javascript.md) — in depth · first look in [14.3 GUIs and other directions](ch14-beyond/03-guis-and-beyond.md) · the GUI dispatcher in [42.4 Desktop GUIs — JavaFX and tkinter](ch42-web-gui/04-desktop-gui.md)

Evol-Instruct
:   [32.2 Synthetic data generation](ch32-data/02-synthetic-data.md) · [Appendix E](appendix/E-ai-glossary.md#s)

exact match
:   [33.1 Benchmarks and what they measure](ch33-eval/01-benchmarks.md) · [Appendix E](appendix/E-ai-glossary.md#e)

exception
:   [10.2 Exceptions — try, except, finally](ch10-exceptions/02-exceptions.md) · reading the failure in [10.3 Reading stack traces](ch10-exceptions/03-stack-traces.md) · [Appendix C](appendix/C-glossary.md#e)

exit code
:   [10.1 Command-line programs and arguments](ch10-exceptions/01-cli-programs.md) · how the shell uses it in [40.1 Bash scripting](ch40-toolchain/01-bash.md)

express lane (skip list)
:   [36.4 Skip lists](ch36-hashing-tries/04-skip-lists.md)

## F

f-string
:   [3.4 Formatting output](ch03-functions/04-output-formatting.md)

feed-forward network
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md)

fetch–decode–execute cycle
:   [0.1 What is a computer, really](ch00-machine/01-hardware.md)

FIFO
:   [19.3 Queues](ch19-stacks-queues/03-queues.md) — see also **queue**

file mode (`"r"`, `"w"`, `"a"`)
:   [11.2 Reading and writing files](ch11-files/02-read-write.md)

file permissions
:   [40.2 SSH and remote development](ch40-toolchain/02-ssh-remote.md) · numeric modes in [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

`filter`
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md)

finite differences
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

fixture (test)
:   [40.4 JUnit and testing at scale](ch40-toolchain/04-junit.md) — lifecycle annotations · pytest style in [24.2 Testing beyond the basics](ch24-practice/02-testing.md)

FlashAttention
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md) · [Appendix E](appendix/E-ai-glossary.md#f)

flexbox
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md)

floating point
:   [5.1 Overflow and floating-point pitfalls](ch05-under-the-hood/01-numeric-pitfalls.md) — in depth · first look in [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) · [Appendix C](appendix/C-glossary.md#f)

Floyd–Warshall algorithm
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md)

`for` loop
:   [6.2 for loops and ranges](ch06-loops/02-for.md) · what `for` really does in [19.1 Iterators](ch19-stacks-queues/01-iterators.md)

frame (stack)
:   [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md) · traced in [17.1 The call stack](ch17-recursion/01-call-stack.md) · [Appendix C](appendix/C-glossary.md#f)

function
:   [3.3 Writing your own functions](ch03-functions/03-writing-functions.md) · [Appendix C](appendix/C-glossary.md#f)

function calling (LLM tools)
:   [28.1 Function calling and JSON Schema](ch28-tools-mcp/01-function-calling.md) · [Appendix E](appendix/E-ai-glossary.md#f)

## G

garbage collection
:   [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md) — first look · reference counting and cycles in [23.2 The memory layout of a program](ch23-os/02-memory-layout.md) · [Appendix C](appendix/C-glossary.md#g)

generator
:   [19.1 Iterators](ch19-stacks-queues/01-iterators.md) — first look · pipelines in [39.3 Generators, pipelines, and Unix pipes](ch39-streams/03-pipelines.md)

generics
:   [18.1 Abstract data types and generics](ch18-linked-lists/01-adts-generics.md) · [Appendix C](appendix/C-glossary.md#g)

GGUF
:   [27.4 Quantization and deployment](ch27-inference/04-quantization-deploy.md) · [Appendix E](appendix/E-ai-glossary.md#g)

Git
:   [1.3 Git and version control, first taste](ch01-tools/03-git.md) — first taste · the daily workflow in [24.1 A real Git workflow](ch24-practice/01-git-workflow.md) · commands in [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

Goodhart's law
:   [33.1 Benchmarks and what they measure](ch33-eval/01-benchmarks.md) · the same failure as reward hacking in [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md)

GPTQ
:   [27.4 Quantization and deployment](ch27-inference/04-quantization-deploy.md) · [Appendix E](appendix/E-ai-glossary.md#g)

GQA (grouped-query attention)
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md) · [Appendix E](appendix/E-ai-glossary.md#g)

gradient
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

graph
:   [37.1 Representing graphs](ch37-graphs/01-representations.md) · preview in [25.1 A preview of Programming III](ch25-next/01-cs400-preview.md) · [Appendix C](appendix/C-glossary.md#g)

GraphRAG
:   [29.4 Knowledge graphs and GraphRAG](ch29-memory-rag/04-graphrag.md) · [Appendix E](appendix/E-ai-glossary.md#g)

greedy decoding
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) · [Appendix E](appendix/E-ai-glossary.md#g)

greedy vs lazy quantifier
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md)

group-relative advantage
:   [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md)

GRPO (Group Relative Policy Optimization)
:   [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md) · [Appendix E](appendix/E-ai-glossary.md#g)

GUI (graphical user interface)
:   [42.4 Desktop GUIs — JavaFX and tkinter](ch42-web-gui/04-desktop-gui.md) — in depth · first look in [14.3 GUIs and other directions](ch14-beyond/03-guis-and-beyond.md)

## H

hash flooding
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

hash function
:   [36.1 Hash tables from scratch](ch36-hashing-tries/01-hash-tables.md) · [Appendix C](appendix/C-glossary.md#h)

hash map
:   [36.1 Hash tables from scratch](ch36-hashing-tries/01-hash-tables.md) — see also **dictionary**

hash table
:   [36.1 Hash tables from scratch](ch36-hashing-tries/01-hash-tables.md) · preview in [25.1 A preview of Programming III](ch25-next/01-cs400-preview.md) · [Appendix C](appendix/C-glossary.md#h)

header (HTTP)
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

heap (data structure)
:   [21.1 The heap property](ch21-heaps/01-heap-property.md) · [Appendix C](appendix/C-glossary.md#h)

heap (memory region)
:   [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md) · in the process address space in [23.2 The memory layout of a program](ch23-os/02-memory-layout.md) · [Appendix C](appendix/C-glossary.md#h)

heap property
:   [21.1 The heap property](ch21-heaps/01-heap-property.md)

heapsort
:   [21.2 Priority queues and heapsort](ch21-heaps/02-priority-queues.md)

height (of a tree)
:   [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md) · the AVL bound in [35.2 AVL trees](ch35-balanced-trees/02-avl.md)

hexadecimal
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) · conversions in [2.2 Number systems](ch02-data/02-number-systems.md)

higher-order function
:   [39.1 Lambdas and higher-order functions](ch39-streams/01-lambdas.md)

hit testing
:   [42.4 Desktop GUIs — JavaFX and tkinter](ch42-web-gui/04-desktop-gui.md)

HNSW
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md) · [Appendix E](appendix/E-ai-glossary.md#h)

HTML
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md)

HTTP
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md) · used end to end in [Project 10 · Full-Stack Mini App](projects/10-fullstack-app/README.md)

hybrid search
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md) · [Appendix E](appendix/E-ai-glossary.md#h)

## I

identity
:   [4.3 Equality vs identity](ch04-branching/03-equality-identity.md) · [Appendix C](appendix/C-glossary.md#i)

`if` statement
:   [4.2 if, elif, else](ch04-branching/02-if-else.md)

`import`
:   [5.4 Overloading, chaining, and imports](ch05-under-the-hood/04-overloading-imports.md)

indentation as syntax
:   [4.2 if, elif, else](ch04-branching/02-if-else.md) · the Java contrast in [5.2 Short-circuits, compound assignment, gotchas](ch05-under-the-hood/02-shortcuts-gotchas.md)

index (position in a sequence)
:   [7.1 Arrays vs Python lists](ch07-arrays/01-arrays-vs-lists.md) · string indexing in [3.2 Strings](ch03-functions/02-strings.md)

infinity and `NaN`
:   [5.1 Overflow and floating-point pitfalls](ch05-under-the-hood/01-numeric-pitfalls.md)

inheritance
:   [15.1 Inheritance](ch15-inheritance/01-inheritance.md) · [Appendix C](appendix/C-glossary.md#i)

in-order traversal
:   [20.3 Traversals and the balance problem](ch20-bst/03-traversals-balance.md)

insertion sort
:   [22.1 Elementary sorts](ch22-sorting/01-elementary-sorts.md) — in depth · first look in [8.3 First algorithms — sort and search](ch08-grids/03-first-algorithms.md)

instance
:   [12.1 Anatomy of a class](ch12-classes/01-class-anatomy.md) · [Appendix C](appendix/C-glossary.md#i)

interface
:   [15.3 Interfaces and abstract classes](ch15-inheritance/03-interfaces.md) · [Appendix C](appendix/C-glossary.md#i)

interpreter
:   [0.3 What is a program — compilers and interpreters](ch00-machine/03-programs.md) · the CPython pipeline in [23.3 Interpreters and virtual machines](ch23-os/03-interpreters-vms.md) · [Appendix C](appendix/C-glossary.md#i)

invariant
:   [13.1 Encapsulation and access control](ch13-design/01-encapsulation.md) — the idea · the BST invariant in [20.2 BST operations](ch20-bst/02-bst-ops.md) · [Appendix C](appendix/C-glossary.md#i)

`is` operator
:   [4.3 Equality vs identity](ch04-branching/03-equality-identity.md) — see also **equality (`==`) vs identity (`is`)**

iterator
:   [19.1 Iterators](ch19-stacks-queues/01-iterators.md) · [Appendix C](appendix/C-glossary.md#i)

`itertools`
:   [39.3 Generators, pipelines, and Unix pipes](ch39-streams/03-pipelines.md)

IVF index
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md)

## J

Java Streams
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md)

JavaScript
:   [42.3 JavaScript in the browser](ch42-web-gui/03-javascript.md)

JIT compiler
:   [23.3 Interpreters and virtual machines](ch23-os/03-interpreters-vms.md) · [Appendix C](appendix/C-glossary.md#j)

JSON-RPC 2.0
:   [28.3 The Model Context Protocol](ch28-tools-mcp/03-mcp-protocol.md) · [Appendix E](appendix/E-ai-glossary.md#j)

JSON Schema
:   [28.1 Function calling and JSON Schema](ch28-tools-mcp/01-function-calling.md) · [Appendix E](appendix/E-ai-glossary.md#j)

JUnit
:   [40.4 JUnit and testing at scale](ch40-toolchain/04-junit.md) · annotation reference in [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

## K

kernel vs user space
:   [23.1 What an operating system does](ch23-os/01-os-processes.md)

keyword argument
:   [5.4 Overloading, chaining, and imports](ch05-under-the-hood/04-overloading-imports.md)

KL penalty
:   [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md) — in PPO · implicit in the DPO objective in [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md) · [Appendix E](appendix/E-ai-glossary.md#k)

knowledge graph
:   [29.4 Knowledge graphs and GraphRAG](ch29-memory-rag/04-graphrag.md)

Kruskal's algorithm
:   [37.4 Minimum spanning trees](ch37-graphs/04-mst.md)

KV cache
:   [27.1 The KV cache](ch27-inference/01-kv-cache.md) · what MHA/MQA/GQA do to its size in [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md) · [Appendix E](appendix/E-ai-glossary.md#k)

## L

`lambda`
:   [39.1 Lambdas and higher-order functions](ch39-streams/01-lambdas.md)

late binding
:   [39.1 Lambdas and higher-order functions](ch39-streams/01-lambdas.md)

layer normalization
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md)

laziness
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md) — first look · measured in [39.3 Generators, pipelines, and Unix pipes](ch39-streams/03-pipelines.md)

leaf
:   [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md)

level-order traversal
:   [20.3 Traversals and the balance problem](ch20-bst/03-traversals-balance.md)

LIFO
:   [19.2 Stacks](ch19-stacks-queues/02-stacks.md) — see also **stack (data structure)**

linear probing
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

linear search
:   [8.3 First algorithms — sort and search](ch08-grids/03-first-algorithms.md) — first look · costed against binary search in [22.3 Searching](ch22-sorting/03-searching.md)

linked list
:   [18.2 Singly linked lists](ch18-linked-lists/02-singly-linked.md) · the doubly linked version in [18.3 Doubly linked lists](ch18-linked-lists/03-doubly-linked.md) · [Appendix C](appendix/C-glossary.md#l)

list (Python)
:   [7.1 Arrays vs Python lists](ch07-arrays/01-arrays-vs-lists.md) · how it grows in [9.2 Dynamic lists — ArrayList and list](ch09-collections/02-dynamic-lists.md) · [Appendix C](appendix/C-glossary.md#l)

LLM-as-a-judge
:   [33.3 LLM-as-a-judge](ch33-eval/03-llm-as-judge.md) · [Appendix E](appendix/E-ai-glossary.md#l)

load factor
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

logits
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) · masked for grammars in [28.2 Structured output and constrained decoding](ch28-tools-mcp/02-structured-output.md) · [Appendix E](appendix/E-ai-glossary.md#l)

lookahead and lookbehind
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md)

loop
:   [6.1 while and do-while](ch06-loops/01-while.md) · counted loops in [6.2 for loops and ranges](ch06-loops/02-for.md) · [Appendix C](appendix/C-glossary.md#l)

LSH (locality-sensitive hashing)
:   [32.4 Filtering, dedup, and verification](ch32-data/04-filtering.md) · [Appendix E](appendix/E-ai-glossary.md#m)

## M

Make
:   [40.3 Make and build systems](ch40-toolchain/03-make.md) · syntax card in [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

`map`
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md)

map (data structure)
:   [14.1 Sets, maps, and dictionaries](ch14-beyond/01-collections-tour.md) — see also **dictionary**

`match` statement
:   [4.4 switch/match, debugging, and style](ch04-branching/04-switch-style-debug.md)

MCP (Model Context Protocol)
:   [28.3 The Model Context Protocol](ch28-tools-mcp/03-mcp-protocol.md) — the protocol · a production server in [28.4 Writing a real MCP server](ch28-tools-mcp/04-building-mcp-server.md) · built in [Project 5 · Mini MCP Server and Client](projects/05-mcp-server/README.md)

memoization
:   [17.2 Classic recursive problems](ch17-recursion/02-classic-recursion.md)

merge conflict
:   [24.1 A real Git workflow](ch24-practice/01-git-workflow.md)

merge sort
:   [22.2 Merge sort and quicksort](ch22-sorting/02-merge-quick.md) · visualised in [Project 4 · Sorting Visualizer](projects/04-sorting-visualizer/README.md)

method
:   [3.1 Using objects and their methods](ch03-functions/01-using-objects.md) · [Appendix C](appendix/C-glossary.md#m)

method overloading
:   [5.4 Overloading, chaining, and imports](ch05-under-the-hood/04-overloading-imports.md) · [Appendix C](appendix/C-glossary.md#o)

method resolution order (MRO)
:   [15.1 Inheritance](ch15-inheritance/01-inheritance.md)

MHA / MQA (attention variants)
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md) · [Appendix E](appendix/E-ai-glossary.md#g)

microtask
:   [42.3 JavaScript in the browser](ch42-web-gui/03-javascript.md)

middleware
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

MinHash
:   [32.4 Filtering, dedup, and verification](ch32-data/04-filtering.md) · [Appendix E](appendix/E-ai-glossary.md#m)

minimum spanning tree (MST)
:   [37.4 Minimum spanning trees](ch37-graphs/04-mst.md)

model collapse
:   [32.2 Synthetic data generation](ch32-data/02-synthetic-data.md) · [Appendix E](appendix/E-ai-glossary.md#m)

modulo
:   [2.3 Operators, precedence, and modulo](ch02-data/03-operators.md) · [Appendix C](appendix/C-glossary.md#m)

MRR (mean reciprocal rank)
:   [29.2 The RAG pipeline](ch29-memory-rag/02-rag-pipeline.md)

multi-agent system
:   [30.3 Multi-agent systems](ch30-agents/03-multi-agent.md) · [Appendix E](appendix/E-ai-glossary.md#m)

multi-head attention
:   [26.2 Embeddings and attention](ch26-llm-internals/02-attention.md) · the KV-cost variants in [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md)

mutation vs rebinding
:   [8.2 Arrays and functions together](ch08-grids/02-arrays-functions.md) · the reference model behind it in [9.1 Values vs references](ch09-collections/01-references.md) · [Appendix C](appendix/C-glossary.md#m)

## N

named group (regex)
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md)

`NaN`
:   [5.1 Overflow and floating-point pitfalls](ch05-under-the-hood/01-numeric-pitfalls.md)

near-duplicate detection
:   [32.4 Filtering, dedup, and verification](ch32-data/04-filtering.md)

negative edge weight
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md)

nested loop
:   [6.3 Nested loops, break, continue](ch06-loops/03-nested-break-continue.md) · over a grid in [8.1 Two-dimensional arrays](ch08-grids/01-2d-arrays.md)

node (linked list)
:   [18.2 Singly linked lists](ch18-linked-lists/02-singly-linked.md) · tree nodes in [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md)

nucleus sampling
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) — see also **top-p sampling (nucleus)**

## O

object
:   [3.1 Using objects and their methods](ch03-functions/01-using-objects.md) · in memory in [9.3 Objects in memory — two views of OOP](ch09-collections/03-objects-in-memory.md) · [Appendix C](appendix/C-glossary.md#o)

off-by-one error
:   [22.3 Searching](ch22-sorting/03-searching.md)

open addressing
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

operator precedence
:   [2.3 Operators, precedence, and modulo](ch02-data/03-operators.md) · the regex version of the same trap in [41.1 Regex fundamentals](ch41-regex/01-fundamentals.md)

orchestrator–worker pattern
:   [30.3 Multi-agent systems](ch30-agents/03-multi-agent.md)

ORM (outcome reward model)
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md) · [Appendix E](appendix/E-ai-glossary.md#p)

out-of-bounds access
:   [7.1 Arrays vs Python lists](ch07-arrays/01-arrays-vs-lists.md)

over-allocation
:   [9.2 Dynamic lists — ArrayList and list](ch09-collections/02-dynamic-lists.md) · the amortized argument in [16.3 The complexity zoo](ch16-complexity/03-complexity-zoo.md)

overflow
:   [5.1 Overflow and floating-point pitfalls](ch05-under-the-hood/01-numeric-pitfalls.md) · [Appendix C](appendix/C-glossary.md#o)

## P

PagedAttention
:   [27.2 Batching, PagedAttention, chunked prefill](ch27-inference/02-batching.md) · [Appendix E](appendix/E-ai-glossary.md#p)

parallel arrays
:   [7.2 Traversal patterns and parallel arrays](ch07-arrays/02-traversal-patterns.md)

parameter
:   [3.3 Writing your own functions](ch03-functions/03-writing-functions.md) · [Appendix C](appendix/C-glossary.md#p)

parameterized test
:   [24.2 Testing beyond the basics](ch24-practice/02-testing.md) · JUnit's version in [40.4 JUnit and testing at scale](ch40-toolchain/04-junit.md)

pass@k
:   [33.1 Benchmarks and what they measure](ch33-eval/01-benchmarks.md) · [Appendix E](appendix/E-ai-glossary.md#p)

path (absolute and relative)
:   [11.1 Paths and the file system](ch11-files/01-paths.md)

path compression
:   [37.4 Minimum spanning trees](ch37-graphs/04-mst.md) — see also **union-find (disjoint sets)**

PEP 8
:   [24.3 Style, reviews, and readable code](ch24-practice/03-style-review.md)

pivot (quicksort)
:   [22.2 Merge sort and quicksort](ch22-sorting/02-merge-quick.md)

planning
:   [30.2 Planning and reflection](ch30-agents/02-planning-reflection.md)

pointer surgery
:   [18.2 Singly linked lists](ch18-linked-lists/02-singly-linked.md) · the four-pointer version in [18.3 Doubly linked lists](ch18-linked-lists/03-doubly-linked.md)

policy (agent loop)
:   [30.1 The agent loop and ReAct](ch30-agents/01-agent-loop-react.md) — the function that chooses the next action

policy (reinforcement learning)
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md) · trained in [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md) · [Appendix E](appendix/E-ai-glossary.md#p)

polymorphism
:   [15.2 Polymorphism and casting](ch15-inheritance/02-polymorphism.md) · [Appendix C](appendix/C-glossary.md#p)

port forwarding
:   [40.2 SSH and remote development](ch40-toolchain/02-ssh-remote.md)

position bias
:   [33.3 LLM-as-a-judge](ch33-eval/03-llm-as-judge.md)

positional encoding
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md) — see also **RoPE (rotary position embedding)**

PPO (Proximal Policy Optimization)
:   [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md) · [Appendix E](appendix/E-ai-glossary.md#p)

pre-order and post-order traversal
:   [20.3 Traversals and the balance problem](ch20-bst/03-traversals-balance.md)

prefill and decode
:   [27.1 The KV cache](ch27-inference/01-kv-cache.md) · [Appendix E](appendix/E-ai-glossary.md#p)

prefix caching
:   [27.1 The KV cache](ch27-inference/01-kv-cache.md) · keeping the prefix stable in [29.3 Agent memory and context management](ch29-memory-rag/03-agent-memory.md)

prefix query
:   [36.3 Tries](ch36-hashing-tries/03-tries.md)

prerequisite (Make)
:   [40.3 Make and build systems](ch40-toolchain/03-make.md)

primitive vs reference type
:   [9.1 Values vs references](ch09-collections/01-references.md)

Prim's algorithm
:   [37.4 Minimum spanning trees](ch37-graphs/04-mst.md)

priority queue
:   [21.2 Priority queues and heapsort](ch21-heaps/02-priority-queues.md) · driving Dijkstra in [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md) · [Appendix C](appendix/C-glossary.md#p)

PRM (process reward model)
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md) · [Appendix E](appendix/E-ai-glossary.md#p)

process
:   [23.1 What an operating system does](ch23-os/01-os-processes.md) · [Appendix C](appendix/C-glossary.md#p)

prompt injection
:   [28.1 Function calling and JSON Schema](ch28-tools-mcp/01-function-calling.md) — the dispatcher as security boundary · what a prompt cannot fix in [30.4 The framework landscape](ch30-agents/04-frameworks.md) · [Appendix E](appendix/E-ai-glossary.md#p)

prompt template (MCP primitive)
:   [28.3 The Model Context Protocol](ch28-tools-mcp/03-mcp-protocol.md)

property (Python)
:   [13.1 Encapsulation and access control](ch13-design/01-encapsulation.md)

public-key authentication
:   [40.2 SSH and remote development](ch40-toolchain/02-ssh-remote.md)

pull request
:   [24.1 A real Git workflow](ch24-practice/01-git-workflow.md)

## Q

quantifier (regex)
:   [41.1 Regex fundamentals](ch41-regex/01-fundamentals.md)

quantization
:   [27.4 Quantization and deployment](ch27-inference/04-quantization-deploy.md) · [Appendix E](appendix/E-ai-glossary.md#q)

query, key, value
:   [26.2 Embeddings and attention](ch26-llm-internals/02-attention.md)

queue
:   [19.3 Queues](ch19-stacks-queues/03-queues.md) · driving level-order traversal in [20.3 Traversals and the balance problem](ch20-bst/03-traversals-balance.md) · [Appendix C](appendix/C-glossary.md#q)

quicksort
:   [22.2 Merge sort and quicksort](ch22-sorting/02-merge-quick.md)

quoting and word splitting (shell)
:   [40.1 Bash scripting](ch40-toolchain/01-bash.md) · [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

## R

radix sort
:   [38.2 Counting, radix, and bucket sort](ch38-linear-sorting/02-counting-radix-bucket.md)

radix tree
:   [36.3 Tries](ch36-hashing-tries/03-tries.md)

RAG (retrieval-augmented generation)
:   [29.2 The RAG pipeline](ch29-memory-rag/02-rag-pipeline.md) · [Appendix E](appendix/E-ai-glossary.md#r)

raising an exception
:   [10.2 Exceptions — try, except, finally](ch10-exceptions/02-exceptions.md)

RAM versus storage
:   [0.1 What is a computer, really](ch00-machine/01-hardware.md)

`range`
:   [6.2 for loops and ranges](ch06-loops/02-for.md)

ReAct
:   [30.1 The agent loop and ReAct](ch30-agents/01-agent-loop-react.md) · built in [Project 6 · A ReAct Agent from Scratch](projects/06-react-agent/README.md) · [Appendix E](appendix/E-ai-glossary.md#r)

recall@k
:   [29.2 The RAG pipeline](ch29-memory-rag/02-rag-pipeline.md)

reciprocal rank fusion
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md)

recursion
:   [17.1 The call stack](ch17-recursion/01-call-stack.md) · classic problems in [17.2 Classic recursive problems](ch17-recursion/02-classic-recursion.md) · [Appendix C](appendix/C-glossary.md#r)

`RecursionError`
:   [17.1 The call stack](ch17-recursion/01-call-stack.md) · the stack limit that causes it in [23.2 The memory layout of a program](ch23-os/02-memory-layout.md)

red-black tree
:   [35.3 Red-black trees](ch35-balanced-trees/03-red-black.md)

redirection (shell)
:   [40.1 Bash scripting](ch40-toolchain/01-bash.md) · [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

ReDoS
:   [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md) — see also **backtracking, catastrophic**

`reduce`
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md)

refactoring
:   [24.3 Style, reviews, and readable code](ch24-practice/03-style-review.md)

reference
:   [9.1 Values vs references](ch09-collections/01-references.md) · a list argument as a reference in [8.2 Arrays and functions together](ch08-grids/02-arrays-functions.md) · [Appendix C](appendix/C-glossary.md#r)

reference counting
:   [23.2 The memory layout of a program](ch23-os/02-memory-layout.md)

reference model
:   [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md) · [Appendix E](appendix/E-ai-glossary.md#r)

reflection (agent self-critique)
:   [30.2 Planning and reflection](ch30-agents/02-planning-reflection.md) · [Appendix E](appendix/E-ai-glossary.md#r)

regression gate
:   [33.2 Building an eval harness](ch33-eval/02-eval-harness.md) · regression tests in [24.2 Testing beyond the basics](ch24-practice/02-testing.md)

regular expression
:   [41.1 Regex fundamentals](ch41-regex/01-fundamentals.md) · groups and parsing in [41.2 Groups, greediness, and real parsing](ch41-regex/02-groups-parsing.md) · syntax card in [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

rehashing
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

REINFORCE
:   [31.2 Policy gradients and PPO](ch31-rl/02-policy-gradient-ppo.md)

reinforcement learning
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

repetition penalty
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md)

replanning
:   [30.2 Planning and reflection](ch30-agents/02-planning-reflection.md)

repository (Git)
:   [1.3 Git and version control, first taste](ch01-tools/03-git.md)

`__repr__`
:   [12.1 Anatomy of a class](ch12-classes/01-class-anatomy.md) · alongside `__str__` in [15.2 Polymorphism and casting](ch15-inheritance/02-polymorphism.md)

reranking
:   [29.2 The RAG pipeline](ch29-memory-rag/02-rag-pipeline.md) · [Appendix E](appendix/E-ai-glossary.md#r)

residual connection
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md)

resource (MCP primitive)
:   [28.3 The Model Context Protocol](ch28-tools-mcp/03-mcp-protocol.md)

REST
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

return (RL)
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

reward
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

reward hacking
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md) · [Appendix E](appendix/E-ai-glossary.md#r)

reward model
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md) · [Appendix E](appendix/E-ai-glossary.md#r)

RLHF and RLAIF
:   [31.4 Reward models — PRM, RLHF, RLAIF](ch31-rl/04-reward-models.md) · [Appendix E](appendix/E-ai-glossary.md#r)

root (tree)
:   [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md)

RoPE (rotary position embedding)
:   [26.3 The decoder-only stack](ch26-llm-internals/03-decoder-stack.md) · [Appendix E](appendix/E-ai-glossary.md#r)

rotation (tree)
:   [35.1 Rotations](ch35-balanced-trees/01-rotations.md) · [Appendix C](appendix/C-glossary.md#r)

router (HTTP)
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

## S

sampling (text generation)
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md)

scaled dot-product attention
:   [26.2 Embeddings and attention](ch26-llm-internals/02-attention.md)

scheduling
:   [23.1 What an operating system does](ch23-os/01-os-processes.md) — the OS · per-iteration scheduling for LLM serving in [27.2 Batching, PagedAttention, chunked prefill](ch27-inference/02-batching.md)

selection sort
:   [8.3 First algorithms — sort and search](ch08-grids/03-first-algorithms.md) — first look · counted and compared in [22.1 Elementary sorts](ch22-sorting/01-elementary-sorts.md)

`self`
:   [12.1 Anatomy of a class](ch12-classes/01-class-anatomy.md)

self-consistency
:   [30.2 Planning and reflection](ch30-agents/02-planning-reflection.md) · [Appendix E](appendix/E-ai-glossary.md#s)

Self-Instruct
:   [32.2 Synthetic data generation](ch32-data/02-synthetic-data.md) · [Appendix E](appendix/E-ai-glossary.md#s)

semantic HTML
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md)

sentinel node
:   [18.3 Doubly linked lists](ch18-linked-lists/03-doubly-linked.md) · the loop-sentinel sense in [6.1 while and do-while](ch06-loops/01-while.md) · [Appendix C](appendix/C-glossary.md#s)

session
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

set (collection)
:   [14.1 Sets, maps, and dictionaries](ch14-beyond/01-collections-tour.md)

`set -euo pipefail`
:   [40.1 Bash scripting](ch40-toolchain/01-bash.md)

shell
:   [1.1 The command line](ch01-tools/01-command-line.md) — using it · scripting it in [40.1 Bash scripting](ch40-toolchain/01-bash.md)

short-circuit evaluation
:   [5.2 Short-circuits, compound assignment, gotchas](ch05-under-the-hood/02-shortcuts-gotchas.md) · [Appendix C](appendix/C-glossary.md#s)

shortest path
:   [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md) — weighted · unweighted, with BFS, in [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md)

sift up / sift down
:   [21.2 Priority queues and heapsort](ch21-heaps/02-priority-queues.md)

skip list
:   [36.4 Skip lists](ch36-hashing-tries/04-skip-lists.md)

slicing
:   [3.2 Strings](ch03-functions/02-strings.md) · the slice-copy idiom in [9.1 Values vs references](ch09-collections/01-references.md)

softmax
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) · as a policy in [31.1 RL from first principles](ch31-rl/01-rl-basics.md)

sorting
:   [22.1 Elementary sorts](ch22-sorting/01-elementary-sorts.md) · [22.2 Merge sort and quicksort](ch22-sorting/02-merge-quick.md) · costs collected in [Appendix B · Big-O reference](appendix/B-big-o.md)

span (tracing)
:   [30.4 The framework landscape](ch30-agents/04-frameworks.md)

specificity (CSS)
:   [42.1 HTML and CSS](ch42-web-gui/01-html-css.md)

SSE (Server-Sent Events)
:   [27.3 Latency, throughput, and streaming](ch27-inference/03-latency-streaming.md) · [Appendix E](appendix/E-ai-glossary.md#s)

SSH
:   [40.2 SSH and remote development](ch40-toolchain/02-ssh-remote.md) · [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

stability (of a sort)
:   [22.1 Elementary sorts](ch22-sorting/01-elementary-sorts.md) · why radix sort needs it in [38.2 Counting, radix, and bucket sort](ch38-linear-sorting/02-counting-radix-bucket.md) · [Appendix C](appendix/C-glossary.md#s)

stack (data structure)
:   [19.2 Stacks](ch19-stacks-queues/02-stacks.md) · used to derecurse in [17.3 Recursion vs iteration](ch17-recursion/03-vs-iteration.md) · [Appendix C](appendix/C-glossary.md#s)

stack (memory region)
:   [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md) · in the process address space in [23.2 The memory layout of a program](ch23-os/02-memory-layout.md)

stack frame
:   [5.3 The stack and the heap](ch05-under-the-hood/03-stack-heap.md) — see also **frame (stack)**

stack trace
:   [10.3 Reading stack traces](ch10-exceptions/03-stack-traces.md) · [Appendix C](appendix/C-glossary.md#s)

staging area (Git)
:   [1.3 Git and version control, first taste](ch01-tools/03-git.md)

statelessness (HTTP)
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

status code (HTTP)
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

`StopIteration`
:   [19.1 Iterators](ch19-stacks-queues/01-iterators.md)

streaming
:   [27.3 Latency, throughput, and streaming](ch27-inference/03-latency-streaming.md) · what it is at the token level in [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md)

string
:   [3.2 Strings](ch03-functions/02-strings.md) · [Appendix C](appendix/C-glossary.md#s)

structured output
:   [28.2 Structured output and constrained decoding](ch28-tools-mcp/02-structured-output.md) · [Appendix E](appendix/E-ai-glossary.md#s)

subtree
:   [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md)

summarization (of context)
:   [29.3 Agent memory and context management](ch29-memory-rag/03-agent-memory.md)

`super()`
:   [15.1 Inheritance](ch15-inheritance/01-inheritance.md)

`switch` statement (Java)
:   [4.4 switch/match, debugging, and style](ch04-branching/04-switch-style-debug.md)

synthetic data
:   [32.2 Synthetic data generation](ch32-data/02-synthetic-data.md) · [Appendix E](appendix/E-ai-glossary.md#s)

`sys.argv`
:   [10.1 Command-line programs and arguments](ch10-exceptions/01-cli-programs.md)

system call
:   [23.1 What an operating system does](ch23-os/01-os-processes.md)

## T

tail recursion
:   [17.3 Recursion vs iteration](ch17-recursion/03-vs-iteration.md)

target (Make)
:   [40.3 Make and build systems](ch40-toolchain/03-make.md)

temperature (sampling)
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) · [Appendix E](appendix/E-ai-glossary.md#s)

test double (stub, mock, fake)
:   [40.4 JUnit and testing at scale](ch40-toolchain/04-junit.md)

thought, action, observation
:   [30.1 The agent loop and ReAct](ch30-agents/01-agent-loop-react.md)

thread
:   [23.1 What an operating system does](ch23-os/01-os-processes.md) · the single-threaded browser in [42.3 JavaScript in the browser](ch42-web-gui/03-javascript.md)

throughput
:   [27.3 Latency, throughput, and streaming](ch27-inference/03-latency-streaming.md) · [Appendix E](appendix/E-ai-glossary.md#t)

tmux
:   [40.2 SSH and remote development](ch40-toolchain/02-ssh-remote.md) · [Appendix F · Toolchain quick reference](appendix/F-toolchain-reference.md)

token (authentication)
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md)

token (LLM)
:   [26.1 From text to tokens](ch26-llm-internals/01-tokenization.md) · [Appendix E](appendix/E-ai-glossary.md#t)

tokenizer
:   [26.1 From text to tokens](ch26-llm-internals/01-tokenization.md) · [Appendix E](appendix/E-ai-glossary.md#t)

tombstone
:   [36.2 Collisions and resizing](ch36-hashing-tries/02-collisions-resizing.md)

tool (MCP primitive)
:   [28.3 The Model Context Protocol](ch28-tools-mcp/03-mcp-protocol.md) · designing tools a model can use in [28.4 Writing a real MCP server](ch28-tools-mcp/04-building-mcp-server.md)

top-k sampling
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) · [Appendix E](appendix/E-ai-glossary.md#t)

top-p sampling (nucleus)
:   [26.4 Sampling — how text is chosen](ch26-llm-internals/04-sampling.md) · [Appendix E](appendix/E-ai-glossary.md#n)

topological sort
:   [37.2 Breadth-first and depth-first search](ch37-graphs/02-traversal.md) · applied to build order in [40.3 Make and build systems](ch40-toolchain/03-make.md)

TPOT (time per output token)
:   [27.3 Latency, throughput, and streaming](ch27-inference/03-latency-streaming.md)

traceback
:   [10.3 Reading stack traces](ch10-exceptions/03-stack-traces.md)

tracing (observability)
:   [30.4 The framework landscape](ch30-agents/04-frameworks.md)

trajectory
:   [31.1 RL from first principles](ch31-rl/01-rl-basics.md) — the RL object · collecting and cleaning it in [32.3 Agent trajectory data](ch32-data/03-trajectories.md) · [Appendix E](appendix/E-ai-glossary.md#t)

traversal (of a tree)
:   [20.3 Traversals and the balance problem](ch20-bst/03-traversals-balance.md) · array traversal patterns in [7.2 Traversal patterns and parallel arrays](ch07-arrays/02-traversal-patterns.md) · [Appendix C](appendix/C-glossary.md#t)

tree
:   [20.1 Tree vocabulary](ch20-bst/01-tree-vocab.md)

trie
:   [36.3 Tries](ch36-hashing-tries/03-tries.md)

triple (subject, relation, object)
:   [29.4 Knowledge graphs and GraphRAG](ch29-memory-rag/04-graphrag.md)

true division vs floor division
:   [2.3 Operators, precedence, and modulo](ch02-data/03-operators.md)

truth table
:   [4.1 Booleans and logic](ch04-branching/01-booleans-logic.md)

`try` / `except` / `finally`
:   [10.2 Exceptions — try, except, finally](ch10-exceptions/02-exceptions.md)

TTFT (time to first token)
:   [27.3 Latency, throughput, and streaming](ch27-inference/03-latency-streaming.md)

tuple
:   [14.1 Sets, maps, and dictionaries](ch14-beyond/01-collections-tour.md)

two-dimensional array
:   [8.1 Two-dimensional arrays](ch08-grids/01-2d-arrays.md)

two's complement
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) · [Appendix C](appendix/C-glossary.md#t)

type
:   [2.1 Variables and types](ch02-data/01-variables-types.md) · [Appendix C](appendix/C-glossary.md#t)

## U

UML class diagram
:   [13.2 UML class diagrams](ch13-design/02-uml.md) · [Appendix C](appendix/C-glossary.md#u)

Unicode
:   [0.2 Bits, binary, and how data is stored](ch00-machine/02-binary.md) · `encoding="utf-8"` in [11.2 Reading and writing files](ch11-files/02-read-write.md)

union-find (disjoint sets)
:   [37.4 Minimum spanning trees](ch37-graphs/04-mst.md)

unit test
:   [8.4 Unit testing](ch08-grids/04-unit-testing.md) · practices that scale in [24.2 Testing beyond the basics](ch24-practice/02-testing.md) · [Appendix C](appendix/C-glossary.md#u)

Unix pipe
:   [39.3 Generators, pipelines, and Unix pipes](ch39-streams/03-pipelines.md) · in shell scripts in [40.1 Bash scripting](ch40-toolchain/01-bash.md)

## V

variable
:   [2.1 Variables and types](ch02-data/01-variables-types.md) · [Appendix C](appendix/C-glossary.md#v)

vector search
:   [29.1 Embeddings and vector search](ch29-memory-rag/01-embeddings-vector-search.md) · [Appendix E](appendix/E-ai-glossary.md#v)

verifiable reward
:   [31.3 DPO and GRPO](ch31-rl/03-dpo-grpo.md) — why GRPO suits it · building verifiers in [32.4 Filtering, dedup, and verification](ch32-data/04-filtering.md)

vertex
:   [37.1 Representing graphs](ch37-graphs/01-representations.md)

virtual machine
:   [23.3 Interpreters and virtual machines](ch23-os/03-interpreters-vms.md) · [Appendix C](appendix/C-glossary.md#v)

vocabulary (tokenizer)
:   [26.1 From text to tokens](ch26-llm-internals/01-tokenization.md)

von Neumann architecture
:   [0.1 What is a computer, really](ch00-machine/01-hardware.md)

## W

WebAssembly
:   [23.3 Interpreters and virtual machines](ch23-os/03-interpreters-vms.md)

weighted graph
:   [37.1 Representing graphs](ch37-graphs/01-representations.md) · why weights break BFS in [37.3 Shortest paths](ch37-graphs/03-shortest-paths.md)

`while` loop
:   [6.1 while and do-while](ch06-loops/01-while.md) · when to prefer `for` in [6.2 for loops and ranges](ch06-loops/02-for.md)

widget tree
:   [42.4 Desktop GUIs — JavaFX and tkinter](ch42-web-gui/04-desktop-gui.md)

`with` statement
:   [11.2 Reading and writing files](ch11-files/02-read-write.md)

working directory
:   [11.1 Paths and the file system](ch11-files/01-paths.md) · `pwd` and `cd` in [1.1 The command line](ch01-tools/01-command-line.md)

working, episodic, and semantic memory
:   [29.3 Agent memory and context management](ch29-memory-rag/03-agent-memory.md)

## X

XSS (cross-site scripting)
:   [42.2 HTTP and a web server from scratch](ch42-web-gui/02-http-server.md) · the DOM side in [42.3 JavaScript in the browser](ch42-web-gui/03-javascript.md)

## Z

zero-based indexing
:   [7.1 Arrays vs Python lists](ch07-arrays/01-arrays-vs-lists.md) — see also **index (position in a sequence)**

`zip`
:   [39.2 Map, filter, reduce, and Java Streams](ch39-streams/02-map-filter-reduce.md)
