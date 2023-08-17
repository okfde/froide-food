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
                  <food-detail-request
                    v-for="req in data.requests"
                    :key="req.id"
                    :request="req" />
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
import FoodDetailRequest from './food-detail-request'
import FoodItemMixin from '../lib/mixin'
import FoodDetailMixin from '../lib/detailmixin'
import { renderDate } from '../lib/utils'

export default {
  name: 'FoodDetail',
  components: { FoodLoader, FoodDetailRequest },
  mixins: [FoodItemMixin, FoodDetailMixin],
  props: {
    data: {
      type: Object,
      default: null
    }
    // TODO: should also get userInfo as it's used in deteailmixin (or improve detailmixin)
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
