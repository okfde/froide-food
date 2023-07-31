<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div v-if="data" class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">
            {{ data.name }}
          </h4>
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
              <food-loader v-if="fetching"></food-loader>
              <template v-else>
                <ul v-if="data.requests.length > 0" class="list-unstyled">
                  <li v-for="req in data.requests" :key="req.id">
                    <h5>
                      Anfrage vom {{ renderDate(req.timestamp) }}
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
  name: 'FoodDetail',
  components: { FoodLoader },
  mixins: [FoodItemMixin, FoodDetailMixin],
  props: {
    data: {
      type: Object,
      default: null
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
  },
  watch: {
    data: function (data) {
      if (data && !data.full) {
        this.getDetail(data)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.postcode-input {
  width: 120px;
}

.or-column {
  text-align: center;
  padding: 0.5rem;
}
</style>
