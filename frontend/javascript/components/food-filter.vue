<template>
  <div>
    <div class="row">
      <div class="col-12 mt-3">
        <h6>Filter</h6>
      </div>
    </div>
    <div class="row">
      <div v-for="filter in filters" class="col-12 col-sm-6 col-md-3">
        <label class="filter-label">
          <input type="checkbox"
            @change="$emit('change', filter)"
            :checked="filter.active">
          <span class="fa" :class="filter.icon" aria-hidden="true"></span>
          {{ filter.name }}
        </label>
      </div>
    </div>
    <div class="row">
      <div class="col-12 ms-auto col-md-3 mb-3">
        <div class="d-grid">
          <button class="btn btn-success" @click="$emit('apply')">
            Filter anwenden
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'food-filter',
  props: {
    filters: {
      type: Array
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-label {
  cursor: pointer;
}
</style>
