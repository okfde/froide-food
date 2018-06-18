function renderDate (date) {
  let d = (new Date(date))
  return `${d.getDate()}.${d.getMonth()}.${d.getFullYear()}`
}

export {
  renderDate
}
