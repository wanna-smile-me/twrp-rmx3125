# Copyright (C) 2022 TeamWin Recovery Project
# SPDX-License-Identifier: Apache-2.0
LOCAL_PATH := device/realme/RMX3125
PRODUCT_SHIPPING_API_LEVEL := 30
PRODUCT_USE_DYNAMIC_PARTITIONS := true
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base.mk)
$(call inherit-product, vendor/twrp/config/common.mk)
PRODUCT_COPY_FILES += $(filter-out \
    $(LOCAL_PATH)/recovery/root/vendor/bin/% \
    $(LOCAL_PATH)/recovery/root/vendor/lib64/%, \
    $(call find-copy-subdir-files,*,$(LOCAL_PATH)/recovery/root,recovery/root))
$(call inherit-product, device/realme/RMX3125/stock-prebuilts.mk)
PRODUCT_PACKAGES += fastbootd
PRODUCT_DEVICE := RMX3125
PRODUCT_NAME := twrp_RMX3125
PRODUCT_BRAND := realme
PRODUCT_MODEL := RMX3125
PRODUCT_MANUFACTURER := realme

# Skip standalone compatibility/runtime tests on this recovery-only build host.
PRODUCT_SOURCE_ROOT_DIRS += -cts/tests -cts/hostsidetests -art/test
