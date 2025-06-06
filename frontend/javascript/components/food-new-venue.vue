<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">Details des fehlenden Betriebs</h4>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            @click="$emit('close')" />
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <div v-if="fetching" class="loading">
                <FoodLoader></FoodLoader>
              </div>
              <template v-else-if="error">
                <div class="alert alert-danger">
                  <p>
                    Ein Fehler ist aufgetreten. Der Betrieb kann nicht angefragt
                    werden.
                  </p>
                </div>
              </template>
              <form v-else @submit="formSubmit">
                <p>
                  Falls der Betrieb, dessen Hygienekontrollbericht Sie anfragen
                  wollen, nicht gelistet wird, können Sie hier die Details des
                  Betriebs eintragen.
                </p>
                <div class="mb-3">
                  <label for="new-venue-name">Der Name des Betriebs</label>
                  <input
                    v-model="name"
                    type="text"
                    class="form-control"
                    id="new-venue-name"
                    aria-describedby="new-venue-name-help"
                    placeholder="Name"
                    required />
                </div>
                <div class="mb-3">
                  <label for="new-venue-address">Adresse</label>
                  <input
                    v-model="address"
                    type="text"
                    class="form-control"
                    id="new-venue-address"
                    placeholder="z.B. Hauptstr. 5"
                    required />
                </div>
                <div class="row">
                  <div class="col">
                    <div class="mb-3">
                      <label for="new-venue-plz">PLZ</label>
                      <input
                        v-model="postcode"
                        id="new-venue-plz"
                        type="text"
                        class="form-control"
                        pattern="[0-9]{5}"
                        required />
                    </div>
                  </div>
                  <div class="col">
                    <div class="mb-3">
                      <label for="new-venue-ort">Ort</label>
                      <input
                        v-model="city"
                        id="new-venue-ort"
                        type="text"
                        class="form-control"
                        placeholder="z.B. Berlin"
                        required />
                    </div>
                  </div>
                </div>
                <p class="text-end">
                  <button type="submit" class="btn btn-primary">
                    Betrieb finden und Anfrage stellen
                  </button>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FoodLoader from './food-loader'
import { postData } from '../lib/utils.js'

export default {
  name: 'FoodNewVenue',
  components: { FoodLoader },
  mounted() {},
  data() {
    return {
      fetching: false,
      error: false,
      name: '',
      address: '',
      postcode: '',
      city: ''
    }
  },
  methods: {
    formSubmit(e) {
      e.preventDefault()
      this.findDetail()
    },
    findDetail() {
      this.fetching = true
      postData(
        '/api/v1/venue/',
        {
          name: this.name,
          address: `${this.address}\n${this.postcode} ${this.city}`,
          ident: 'custom',
          requests: []
        },
        this.$root.csrfToken
      ).then((data) => {
        this.fetching = false
        if (data.error !== false) {
          console.warn('Error requesting the API')
          this.error = true
          return
        }
        this.$emit('venuecreated', data['result'])
        this.$emit('close')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.loading {
  padding-top: 3em 0;
  background-color: #fff;
  text-align: center;
}

.loading img {
  width: 10%;
}
</style>
