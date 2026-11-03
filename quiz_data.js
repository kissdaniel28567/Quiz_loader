window.quizData = {
  title: "Theory Test 1 Practice Exam",
  subtitle: "Lectures 1–6 (Machine Learning & Deep Learning Basics) + NumPy Foundations",
  questions: [
    {
      id: 1,
      title: "Question 1: Cholesterol Prediction Task Setup",
      text: "We want to predict the cholesterol level of patients (continuous value) based on weight, age, height, and sex (4 attributes) on a dataset of 200 patients. Which of the following statements are TRUE?",
      options: [
        { id: "A", text: "Linear regression is a more suitable choice than logistic regression for this task." },
        { id: "B", text: "If we use linear regression with an intercept/bias term, the model has 4 parameters." },
        { id: "C", text: "In matrix form h_θ(X) = Xθ (with an intercept column in X), the shape of matrix X is (200, 5)." },
        { id: "D", text: "The age values of the patients are contained within vector θ." },
        { id: "E", text: "During training, our optimization objective is to minimize the matrix X." }
      ],
      correct: ["A", "C"],
      explanation: "A is TRUE (continuous target). B is FALSE (4 features + 1 bias = 5 parameters). C is TRUE (200 samples × 5 columns). D is FALSE (age is a feature in X). E is FALSE (we minimize the cost function J(θ), not X)."
    },
    {
      id: 2,
      title: "Question 2: Convexity & Optimization",
      text: "Which of the following statements regarding the optimization of machine learning models are TRUE?",
      options: [
        { id: "A", text: "In linear regression with Mean Squared Error (MSE), gradient descent with a sufficiently small step size is guaranteed to converge to the globally optimal parameters." },
        { id: "B", text: "In a Multi-Layer Perceptron (MLP) trained with MSE, gradient descent is guaranteed to find the globally optimal parameters given a small enough step size." },
        { id: "C", text: "The loss function J(θ) evaluated over the dataset evaluates to a scalar value." },
        { id: "D", text: "Hyperparameters (e.g., learning rate, number of layers) are typically optimized directly using standard gradient descent (such as SGD)." }
      ],
      correct: ["A", "C"],
      explanation: "A is TRUE (linear regression with MSE is strictly convex). B is FALSE (neural network loss surfaces are non-convex with local minima). C is TRUE (objective loss is a scalar). D is FALSE (hyperparameters are tuned via search strategies, not SGD)."
    },
    {
      id: 3,
      title: "Question 3: Feature Scaling",
      text: "Regarding feature scaling techniques, which of the following statements are TRUE?",
      options: [
        { id: "A", text: "Feature scaling helps gradient descent converge faster by avoiding highly elongated elliptical loss contours." },
        { id: "B", text: "Without feature scaling, gradient descent may oscillate heavily or diverge unless an extremely small learning rate is chosen." },
        { id: "C", text: "Min-max scaling is more robust to extreme outlier data points than standardization (z-score scaling)." },
        { id: "D", text: "Standardization subtracts the sample mean and divides by the standard deviation." }
      ],
      correct: ["A", "B", "D"],
      explanation: "A, B, and D are TRUE. C is FALSE (Min-max scaling directly uses min and max, compressing normal data when an extreme outlier exists; standardization is more robust)."
    },
    {
      id: 4,
      title: "Question 4: Disease Diagnosis (Classification)",
      text: "We want to classify patients as sick or healthy (binary label) based on 2 blood test values with 100 training patients. We use logistic regression h_θ(X) = g(Xθ). Which of the following statements are TRUE?",
      options: [
        { id: "A", text: "Logistic regression with an intercept term will have 3 parameters in total." },
        { id: "B", text: "The range of values in the output vector h_θ(X) is (-∞, +∞)." },
        { id: "C", text: "Binary Cross-Entropy (Log Loss) is the standard loss function for this task." },
        { id: "D", text: "During learning, we aim to minimize the sigmoid function g." }
      ],
      correct: ["A", "C"],
      explanation: "A is TRUE (2 weights + 1 bias = 3 parameters). B is FALSE (sigmoid output is bounded in (0, 1)). C is TRUE. D is FALSE (we minimize the binary cross-entropy cost function J(θ))."
    },
    {
      id: 5,
      title: "Question 5: Multi-Layer Perceptron (MLP) Architecture",
      text: "Consider an MLP estimating a single continuous value from 20 input variables. The network has one hidden layer with 10 neurons, followed by the output layer. Which statements are TRUE?",
      options: [
        { id: "A", text: "There are 210 parameters (weights + biases) in the first (hidden) layer." },
        { id: "B", text: "The entire network has a total of 221 trainable parameters." },
        { id: "C", text: "We should omit the hidden activation function g₁ to keep the model flexible." },
        { id: "D", text: "The output activation function g₂ should be a sigmoid function." },
        { id: "E", text: "The output activation function g₂ should be omitted (or set to the identity function) to predict unbounded continuous values." }
      ],
      correct: ["A", "B", "E"],
      explanation: "A is TRUE (20×10 + 10 = 210). B is TRUE (Layer 2 has 10×1 + 1 = 11; 210 + 11 = 221). C is FALSE (omitting g₁ collapses the MLP into a linear model). D is FALSE (sigmoid restricts output to (0, 1)). E is TRUE (identity output for regression)."
    },
    {
      id: 6,
      title: "Question 6: Overfitting and Regularization",
      text: "Which of the following statements regarding training dynamics and overfitting are TRUE?",
      options: [
        { id: "A", text: "Decreasing the number of training examples generally makes overfitting more severe." },
        { id: "B", text: "Decreasing the number of test examples makes overfitting more severe." },
        { id: "C", text: "Increasing the number of parameters in our neural network increases the risk of overfitting." },
        { id: "D", text: "If validation loss starts increasing while training loss continues decreasing, it indicates overfitting." },
        { id: "E", text: "According to early stopping, we should stop training when the training loss begins to increase." }
      ],
      correct: ["A", "C", "D"],
      explanation: "A is TRUE. B is FALSE (test set size affects evaluation variance, not model overfitting). C is TRUE. D is TRUE. E is FALSE (early stopping triggers when validation loss begins to consistently increase)."
    },
    {
      id: 7,
      title: "Question 7: Backpropagation Computational Graph",
      text: "Consider backpropagation through individual computational graph nodes where grad_c = ∂J/∂c. Which statements are TRUE?",
      options: [
        { id: "A", text: "For a square node c = b², the backpropagated gradient with respect to b is: grad_b = grad_c * 2 * b." },
        { id: "B", text: "For a square node c = b², the backpropagated gradient with respect to b is: grad_b = grad_c * 2 * c." },
        { id: "C", text: "For an addition node c = a + b, the gradients are: grad_a = grad_b = grad_c." },
        { id: "D", text: "For an addition node c = a + b, the gradients are: grad_a = grad_c + b and grad_b = grad_c + a." }
      ],
      correct: ["A", "C"],
      explanation: "By chain rule: ∂J/∂b = (∂J/∂c)(∂c/∂b) = grad_c * (2b), making A TRUE and B FALSE. For c = a + b, ∂c/∂a = 1 and ∂c/∂b = 1, so grad_a = grad_b = grad_c, making C TRUE and D FALSE."
    },
    {
      id: 8,
      title: "Question 8: NumPy Array Shapes & Indexing",
      text: "Let my_array be a numpy.ndarray with shape (32, 5). Which of the following statements are TRUE?",
      options: [
        { id: "A", text: "The expression my_array[:, 1].shape evaluates to (32,)." },
        { id: "B", text: "The expression my_array[[0], :].shape evaluates to (1, 5)." },
        { id: "C", text: "The expression my_array[1, :].shape evaluates to (1, 5)." },
        { id: "D", text: "The expression my_array.shape can validly be equal to 12." },
        { id: "E", text: "The expression my_array[[-1, -1], -1].shape evaluates to (2,)." }
      ],
      correct: ["A", "B", "E"],
      explanation: "A is TRUE (integer indexing drops the axis). B is TRUE (list indexing preserves the 2D shape). C is FALSE (it drops axis 0, yielding shape (5,)). D is FALSE (shape is always a tuple, not an int). E is TRUE (selects 2 elements from the last column)."
    },
    {
      id: 9,
      title: "Question 9: NumPy Broadcasting",
      text: "Let my_array1 have shape (32, 5) and numeric dtype. Which of the following operations will NOT raise a ValueError?",
      options: [
        { id: "A", text: "my_array1 + my_array2, where my_array2 has shape (32,)" },
        { id: "B", text: "my_array1 + my_array2[:, None], where my_array2 has shape (32,)" },
        { id: "C", text: "my_array1 + my_array2[None, :], where my_array2 has shape (32,)" },
        { id: "D", text: "my_array1 + 1" }
      ],
      correct: ["B", "D"],
      explanation: "A raises ValueError ((32, 5) vs (32,): trailing dim 5 != 32). B is valid ((32, 5) + (32, 1) -> (32, 5)). C raises ValueError ((32, 5) + (1, 32): 5 != 32). D is valid (scalar broadcasts to any shape)."
    },
    {
      id: 10,
      title: "Question 10: NumPy Views vs Copies",
      text: "Let my_array = np.arange(4). In which of the following cases will modifying my_array2 via my_array2[:] = 99 ALSO modify the elements of original my_array?",
      options: [
        { id: "A", text: "my_array2 = my_array.reshape(2, 2)" },
        { id: "B", text: "my_array2 = my_array.T" },
        { id: "C", text: "my_array2 = my_array[1:2]" },
        { id: "D", text: "my_array2 = my_array[[1, 2]]" },
        { id: "E", text: "my_array2 = my_array[my_array < 2]" },
        { id: "F", text: "my_array2 = np.append(my_array, 42)" }
      ],
      correct: ["A", "B", "C"],
      explanation: "A, B, and C return VIEWS sharing data buffer with my_array. D (fancy indexing), E (boolean masking), and F (np.append) return COPIES/new arrays, leaving my_array unaffected."
    },
    {
      id: 11,
      title: "Question 11: NumPy Array Analysis Functions",
      text: "Let my_array = np.array([3, 1, 2]). Which of the following statements are TRUE?",
      options: [
        { id: "A", text: "np.unique(my_array) evaluates to array([1, 2, 3])." },
        { id: "B", text: "np.bincount(my_array) evaluates to array([0, 1, 1, 1])." },
        { id: "C", text: "np.argsort(my_array) evaluates to array([1, 2, 0])." },
        { id: "D", text: "np.unique(my_array == 0) evaluates to array([True, False])." }
      ],
      correct: ["A", "B", "C"],
      explanation: "A is TRUE (returns sorted unique elements). B is TRUE (counts occurrences of 0, 1, 2, 3: zero 0s, one 1, one 2, one 3). C is TRUE (indices of sorted elements: 1 is at index 1, 2 at index 2, 3 at index 0). D is FALSE (my_array has no zeros, so array == 0 is all False; unique returns array([False]))."
    }
  ]
};