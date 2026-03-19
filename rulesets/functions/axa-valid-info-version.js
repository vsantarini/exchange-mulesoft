// Copyright AXA 2021. All Rights Reserved.
// This file is licensed under the LOAS-IS License.
module.exports = (targetValue, options) => {
  const regexp = new RegExp(options.versionPattern);

  if (!regexp.test(targetValue)) {
    return [{ message: options.versionPatternDescription }];
  }

  return undefined;
};