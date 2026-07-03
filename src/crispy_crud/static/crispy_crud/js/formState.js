document.addEventListener('alpine:init', () => {
  Alpine.data('formState', () => ({
    form: undefined,
    initialState: undefined,
    isDirty: false,
    init() {
      // find closest form element
      this.form = this.$el.querySelector('form');
      if (!this.form) {
        console.warn('No form found');
        return;
      }

      this.$nextTick(() => {
        // get initial state of form
        this.initialState = this._serializeForm();
        if (this.initialState === '{}') {
          console.warn('Initial form state is empty');
          return;
        }
        // add listener to each form element to detect changes
        this._monitorFormState();
      });
    },
    _serializeForm() {
      const obj = {};

      // Get all form elements
      this.form
        .querySelectorAll('input, select, textarea')
        .forEach((element) => {
          if (element.type === 'checkbox') {
            if (
              document.querySelectorAll(`input[name="${element.name}"]`)
                .length > 1
            ) {
              // Handle multiple checkboxes with same name
              if (!obj[element.name]) {
                obj[element.name] = [];
              }
              if (element.checked) {
                obj[element.name].push(element.value);
              }
            } else {
              // Handle single checkboxes - only set if checked
              if (element.checked) {
                obj[element.name] = 'on';
              } else {
                obj[element.name] = '';
              }
            }
          } else if (element.type !== 'submit' && element.name) {
            obj[element.name] = element.value;
          }
        });

      return JSON.stringify(obj);
    },
    _monitorFormState() {
      const updateDirty = () => {
        this.isDirty = this._serializeForm() !== this.initialState;
      };

      // add listener to each form element to detect changes
      this.form.querySelectorAll('input, select, textarea').forEach((el) => {
        if (el.type === 'submit') return;

        const tag = el.tagName.toLowerCase();

        if (tag === 'textarea') {
          el.addEventListener('input', updateDirty);
          return;
        }

        if (tag === 'select') {
          el.addEventListener('change', updateDirty);
          return;
        }

        if (tag === 'input') {
          switch (el.type) {
            case 'checkbox':
            case 'radio':
            case 'file':
              el.addEventListener('change', updateDirty);
              break;
            default:
              el.addEventListener('input', updateDirty); // updates while focused/typing
              el.addEventListener('change', updateDirty); // fallback on blur
              break;
          }
        }
      });
    },
  }));
});
