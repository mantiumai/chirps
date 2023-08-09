# Account Application
The account application is responsible for handling per-user authentication, preferences, and secrets.

## API Key Workflow
The `/account/profile` view renders all of the user's preferences. In addition, it displays any configured API keys. Each key is individually rendered via the `/account/api_key_<masked|unmasked>` views. Each view returns the HTML needed to display the key in either a masked or unmasked form. For the masked view, a UI element is present to un-mask the API key - which simply makes an HTMX request to replace the existing API key HTML elements with the unmasked version.

In addition, both masked and unmasked views will render an edit button. The edit button opens a modal which allows the user to configure the respective key. Upon a successful submission, the masked-version of the API key is returned and replaced in the DOM.
