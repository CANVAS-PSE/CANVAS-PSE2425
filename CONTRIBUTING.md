# Contributing to CANVAS

Welcome to `CANVAS`:sun_with_face:! We're thrilled that you're interested in contributing to our open-source project :fire:.
By participating, you can help improve the project and make it even better :raised_hands:.

## How to Contribute

1. **Clone the repository**: Clone the repository to your local machine using Git :octocat::

   ```bash
   git clone https://github.com/ARTIST-Association/CANVAS.git
   ```

2. **Install all development dependencies** in a separate python virtual environment from the main branch of your repo.
   This will put a number of pre-commit hooks, for code linting and code style for both Python and JavaScript, into place.
   It will also install tools like ruff and ESLint, used for development.
   Till we completely merged to a pyproject.toml you need to run the following commands:

   ```bash
   # Python environment
   python3 -m venv <insert/path/to/your/venv>
   source <insert/path/to/your/venv/bin/activate>

   # Pre commit hooks
   pre-commit install

   # Dev tools
   cd canvas_editor/
   python -m pip install -r requirements.txt
   npm install
   ```

3. **Open a new issue or choose an existing one**: When opening a new issue choose a fitting label. Assign yourself to the chosen or new issue.
   If the issue is bigger, feel free to create a task list, and even new sub-issues.

4. **Create a Branch**: Create a new branch associated with the issue via the GitHub website and follow the instructions.

5. **Make Changes**: Make your desired changes to the codebase. Please stick to the following guidelines:

   **Python**:
   - Please use type hints in all function definitions.
   - Please use American English for all comments and docstrings in the code.
   - Please use the [NumPy Docstring Standard](https://numpydoc.readthedocs.io/en/latest/format.html) for your docstrings:

   ```python
   """
   Short Description

   Long Description (if needed)

   Parameters
   ----------
   param1 : type
       Description of param1.

   param2 : type, optional
     Description of param2. (if it's an optional argument)

   Returns
   -------
     return_type
       Description of the return value.

   Raises
   ------
     ExceptionType
         Description of when and why this exception might be raised.

   See Also
   --------
     other_function : Related function or module.

   Examples
   --------
       >>> import numpy as np
       >>> x = np.array([1, 2, 3])
       >>> y = np.square(x)
       >>> print(y)
     array([1, 4, 9])

   Notes
   -----
   Additional notes, recommendations, or important information.
   """
   ```

   When applicable, please make references to parent modules and classes using ``:class:`ParentClassName` ``
   as shown below. Do not include attributes and methods of the parent class explicitly.

   ```python
   class ParentClass:
     """
     The docstring for the parent class.

     Attributes
     ----------
     attribute : type
         Description of attribute.

     Methods
     -------
     method()
         Description of method.
     """

   class ChildClass(ParentClass):
     """
     The docstring for the child class.

     Attributes
     ----------
     attribute_child : type
         Description of attribute_child.

     Methods
     ----------
     method_child()
         Description of method_child.

     See Also
     --------
       :class:`ParentClass` : Reference to the parent class.
     """
   ```

   In the example above, `` :class:`ParentClass` `` is used to create a reference to the parent class `ParentClass`.

   **JavaScript**:
   - Use JsDocs for classes and functions, so that ESLint is satisfied
   - Follow the guidelines specified in the `eslint.config.mjs`

6. **Commit Changes**: Commit your changes with a clear and concise commit message that describes what you have changed.
   Example:

   ```bash
   git commit -m "add rotation control for heliostat"
   ```

7. **Push Changes**: Push your changes to your fork on GitHub:

   ```bash
   git push
   ```

   As the remote branch is already linked

8. **Open a Pull Request**: Open a pull request for this branch. The issue should be linked automatically.

## Code of Conduct

Please note that we have a [Code of Conduct](CODE_OF_CONDUCT.md), and we expect all contributors to follow it. Be kind and respectful to one another :blue_heart:.

## Questions or Issues

If you have questions or encounter any issues, please create an issue in the [Issues](https://github.com/ARTIST-Association/ARTIST/issues) section of this repository.

Thank you for your contribution :pray:!
