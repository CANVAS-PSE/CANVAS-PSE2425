/**
 * Base class that provides property subscription and connection to signals of the class.
 * @template {{[key: string]: any}} PropertyBag Type that contains all properties of the extending class.
 * @template {string} SignalNames Type with all signal names of the extending class.
 */
export class Observable {
  /**
   * @protected
   * @type {Map<keyof PropertyBag, Set<(newValue: any) => void>>}
   */
  _propertySubscribers = new Map();

  /**
   * @protected
   * @type {Map<string, Set<() => void>>}
   */
  _signalSubscribers = new Map();

  /**
   * Create a new observable instance.
   * Wraps the extending class with a proxy to provide subscription functionality.
   */
  constructor() {
    // keep a reference of this class to access the property and signal maps
    const self = this;

    // Wrap the object with a proxy to notify subscribers of value changes
    return new Proxy(this, {
      /**
       * Notify all subscribers of the property of the new change.
       * @param {Observable} target the target of the set trap call.
       * @param {string} property the property of the set trap call.
       * @param {PropertyBag[keyof PropertyBag]} value the new value for the property.
       * @returns {boolean} whether the set was successful
       */
      set(target, property, value) {
        const success = Reflect.set(target, property, value);

        if (success && self._propertySubscribers.has(property)) {
          const callbacks = self._propertySubscribers.get(property);

          if (callbacks) {
            callbacks.forEach((callback) => {
              callback(value);
            });
          }
        }

        return success;
      },
    });
  }

  /**
   * Subscribe to changes of the given property.
   * @template {keyof PropertyBag} K
   * @param {K} propertyName The name of the property you want to subscribe to.
   * @param {(newValue: PropertyBag[K]) => void} callback The callback function that is called when the property changes.
   * @returns {() => void} Function to unsubscribe from future changes.
   */
  subscribe(propertyName, callback) {
    if (!this._propertySubscribers.has(propertyName)) {
      this._propertySubscribers.set(propertyName, new Set());
    }

    /** @type {Set<(arg0: any[]) => void>} */
    const callbacks = this._propertySubscribers.get(propertyName);
    callbacks.add(callback);

    return () => {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this._propertySubscribers.delete(propertyName);
      }
    };
  }

  /**
   * Registers a callback to be executed when a named event is emitted.
   * @param {SignalNames} signalName The name of the signal you want to connect to.
   * @param {() => void} callback Callback that is executed when the signal is notified.
   * @returns {() => void} A function to stop listening for future signals.
   */
  connect(signalName, callback) {
    if (!this._signalSubscribers.has(signalName)) {
      this._signalSubscribers.set(signalName, new Set());
    }

    const listeners = this._signalSubscribers.get(signalName);
    listeners.add(callback);

    return () => {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this._signalSubscribers.delete(signalName);
      }
    };
  }

  /**
   * Notifies all who are connect that the signal got called.
   * @param {SignalNames} signalName - The name of the signal you want to call.
   */
  notify(signalName) {
    if (this._signalSubscribers.has(signalName)) {
      this._signalSubscribers.get(signalName).forEach((listener) => {
        listener();
      });
    }
  }
}
