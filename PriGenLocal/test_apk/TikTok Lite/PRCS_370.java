/*Application Package Name: com.tiktok.lite.go
class PRCS_370 {
/**
ms.bd.o.f2;L()V
*/

    public final declared_synchronized void L()
    {
        try {
            if (ms.bd.o.n2.LB() != 1) {
                return;
            } else {
                try {
                    android.hardware.SensorManager v12 = this.LB;
                } catch (java.util.List v1_5) {
                    throw v1_5;
                }
                if (v12 == null) {
                    try {
                        java.math.BigDecimal v7_0 = 0;
                    } catch (com.bytedance.helios.statichook.api.Result v8_0) {
                        java.math.BigDecimal v7_6 = new org.json.JSONArray();
                        v7_6.put(new java.math.BigDecimal(((double) this.LCC[0])).setScale(2, 4));
                        v7_6.put(new java.math.BigDecimal(((double) this.LCC[1])).setScale(2, 4));
                        v7_6.put(new java.math.BigDecimal(((double) this.LCC[2])).setScale(2, 4));
                        this.LBL().LC = 0;
                        throw v8_0;
                    }
                } else {
                    if (this.LBL == 0) {
                        java.util.List v1_63;
                        java.math.BigDecimal v7_4 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        Object[] v13 = new Object[1];
                        v13[0] = Integer.valueOf(1);
                        int v14_2 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", "eSwwXgZ0UITaBw==");
                        java.util.ArrayList v2_5 = v7_4.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, "android.hardware.Sensor", v14_2);
                        if (!v2_5.intercept) {
                            v1_63 = v12.getDefaultSensor(1);
                            v7_4.postInvoke(v1_63, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, v14_2, 1);
                        } else {
                            v7_4.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, v14_2, 0);
                            v1_63 = ((android.hardware.Sensor) v2_5.returnValue);
                        }
                        java.util.List v1_2;
                        int v3_2 = this.LB;
                        com.bytedance.helios.statichook.api.HeliosApiHook v16_4 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                        com.bytedance.helios.statichook.api.Result v8_2 = new Object[3];
                        v8_2[0] = this;
                        v8_2[1] = v1_63;
                        v8_2[2] = Integer.valueOf(3);
                        java.util.ArrayList v2_8 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/hardware/SensorEventListener;Landroid/hardware/Sensor;I)Z", "eSwwXgZ0UITaBw==");
                        Object[] v22_2 = v8_2;
                        com.bytedance.helios.statichook.api.Result v8_3 = v16_4.preInvoke(100700, "android/hardware/SensorManager", "registerListener", v3_2, v8_2, "boolean", v2_8);
                        if (!v8_3.intercept) {
                            v1_2 = v3_2.registerListener(this, v1_63, 3);
                            v16_4.postInvoke(Boolean.valueOf(v1_2), 100700, "android/hardware/SensorManager", "registerListener", v3_2, v22_2, v2_8, 1);
                        } else {
                            v16_4.postInvoke(0, 100700, "android/hardware/SensorManager", "registerListener", v3_2, v22_2, v2_8, 0);
                            v1_2 = ((Boolean) v8_3.returnValue).booleanValue();
                        }
                        if (v1_2 == null) {
                        }
                    }
                    this.LBL = (this.LBL + 1);
                }
            }
        } catch (java.util.List v1_56) {
            throw v1_56;
        }
    }

/**
ms.bd.o.z0;L(I J Ljava/lang/String; Ljava/lang/Object;)Ljava/lang/Object;
*/

    public final Object L(int p2, long p3, String p5, Object p6)
    {
        ms.bd.o.f2.L(ms.bd.o.a.L.LB).L();
        return 0;
    }


}