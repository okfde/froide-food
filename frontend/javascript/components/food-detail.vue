<template>
  <div class="modal-mask" @click.self="$emit('close')">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">
            {{ data.name }}
          </h4>
          <button
            type="button"
            class="close"
            aria-label="Close"
            @click="$emit('close')">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <food-loader v-if="fetching"></food-loader>
              <template v-else>
                <ul v-if="data.requests.length > 0" class="list-unstyled">
                  <li v-for="req in data.requests" :key="req.id">
                    <h5>
                      Anfrage vom {{ req.timestamp | date }}
                      <small class="ms-3">
                        <a :href="req.url" target="_blank">
                          zur Anfrage&nbsp;&rarr;
                        </a>
                      </small>
                    </h5>
                    <p v-if="req.documents.length > 0">
                      Dokumente in dieser Anfrage:
                    </p>
                    <ul v-if="req.documents.length > 0">
                      <li v-for="doc in req.documents" :key="doc.url">
                        <a :href="doc.url" target="_blank">
                          {{ doc.name }}
                        </a>
                      </li>
                    </ul>
                    <p v-else class="text-muted">Noch keine Dokumente.</p>
                  </li>
                </ul>
                <p v-else>Noch keine Anfragen</p>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FoodLoader from './food-loader'
import FoodItemMixin from '../lib/mixin'
import FoodDetailMixin from '../lib/detailmixin'
import { renderDate } from '../lib/utils'

export default {
  name: 'food-detail',
  components: { FoodLoader },
  mixins: [FoodItemMixin, FoodDetailMixin],
  props: {
    data: {
      type: Object
    }
  },
  mounted() {
    if (!this.data.full) {
      this.getDetail(this.data)
    }
  },
  data() {
    return {
      fetching: false
    }
  },
  filters: {
    date: function (d) {
      return renderDate(d)
    }
  }
}
</script>

<style lang="scss" scoped>
#food-locator {
  z-index: 3000;
}

.postcode-input {
  width: 120px;
}

.or-column {
  text-align: center;
  padding: 0.5rem;
}

.modal-mask {
  position: absolute;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  transition: opacity 0.3s ease;
}
.is-embed .modal-mask {
  top: 10px;
}
</style>
