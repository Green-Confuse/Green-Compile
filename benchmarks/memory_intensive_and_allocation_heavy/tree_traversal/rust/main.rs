use std::collections::VecDeque;

#[derive(Debug)]
struct TreeNode<T> {
    value: T,
    left: Option<Box<TreeNode<T>>>,
    right: Option<Box<TreeNode<T>>>,
}

enum TraversalMethod {
    PreOrder,
    InOrder,
    PostOrder,
    LevelOrder,
}

impl TreeNode<i8> {
    pub fn new(arr: &[[i8; 3]]) -> TreeNode<i8> {
        let l = match arr[0][1] {
            -1 => None,
            i => Some(Box::new(TreeNode::new(
                &arr[(i - arr[0][0]) as usize..],
            ))),
        };
        let r = match arr[0][2] {
            -1 => None,
            i => Some(Box::new(TreeNode::new(
                &arr[(i - arr[0][0]) as usize..],
            ))),
        };

        TreeNode {
            value: arr[0][0],
            left: l,
            right: r,
        }
    }

    pub fn traverse(&self, tr: &TraversalMethod) -> Vec<&TreeNode<i8>> {
        match tr {
            TraversalMethod::PreOrder => self.iterative_preorder(),
            TraversalMethod::InOrder => self.iterative_inorder(),
            TraversalMethod::PostOrder => self.iterative_postorder(),
            TraversalMethod::LevelOrder => self.iterative_levelorder(),
        }
    }

    fn iterative_preorder(&self) -> Vec<&TreeNode<i8>> {
        let mut stack = vec![self];
        let mut res = Vec::new();

        while let Some(node) = stack.pop() {
            res.push(node);
            if let Some(r) = node.right.as_deref() {
                stack.push(r);
            }
            if let Some(l) = node.left.as_deref() {
                stack.push(l);
            }
        }
        res
    }

    fn iterative_inorder(&self) -> Vec<&TreeNode<i8>> {
        let mut stack = Vec::new();
        let mut res = Vec::new();
        let mut cur = Some(self);

        while cur.is_some() || !stack.is_empty() {
            while let Some(node) = cur {
                stack.push(node);
                cur = node.left.as_deref();
            }
            let node = stack.pop().unwrap();
            res.push(node);
            cur = node.right.as_deref();
        }
        res
    }

    fn iterative_postorder(&self) -> Vec<&TreeNode<i8>> {
        let mut stack = vec![self];
        let mut res = Vec::new();

        while let Some(node) = stack.pop() {
            res.push(node);
            if let Some(l) = node.left.as_deref() {
                stack.push(l);
            }
            if let Some(r) = node.right.as_deref() {
                stack.push(r);
            }
        }
        res.into_iter().rev().collect()
    }

    fn iterative_levelorder(&self) -> Vec<&TreeNode<i8>> {
        let mut queue = VecDeque::new();
        let mut res = Vec::new();

        queue.push_back(self);
        while let Some(node) = queue.pop_front() {
            res.push(node);
            if let Some(l) = node.left.as_deref() {
                queue.push_back(l);
            }
            if let Some(r) = node.right.as_deref() {
                queue.push_back(r);
            }
        }
        res
    }
}

fn main() {
    let arr_tree = [
        [1, 2, 3],
        [2, 4, 5],
        [3, 6, -1],
        [4, 7, -1],
        [5, -1, -1],
        [6, 8, 9],
        [7, -1, -1],
        [8, -1, -1],
        [9, -1, -1],
    ];

    let root = TreeNode::new(&arr_tree);

    let methods = [
        (TraversalMethod::PreOrder, "pre-order"),
        (TraversalMethod::InOrder, "in-order"),
        (TraversalMethod::PostOrder, "post-order"),
        (TraversalMethod::LevelOrder, "level-order"),
    ];

    for (m, label) in methods {
        print!("{}:", label);
        for n in root.traverse(&m) {
            print!(" {}", n.value);
        }
        println!();
    }
}
