/*Application Package Name: com.tiktok.lite.go
class PRCS_351 {
/**
ms.bd.o.d2;L(I)V
*/

    private declared_synchronized void L(int p26)
    {
        try {
            String v12_0 = this.LI;
        } catch (Exception) {
            return;
        } catch (boolean v0_6) {
            throw v0_6;
        }
        if (v12_0 == null) {
            return;
        } else {
            boolean v0_8;
            com.bytedance.helios.statichook.api.Result v7_3 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            android.hardware.SensorManager v13_1 = new Object[1];
            v13_1[0] = Integer.valueOf(p26);
            Object[] v14_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", "eSwwXgZ0UITYBw==");
            Object[] v2_2 = v7_3.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", v12_0, v13_1, "android.hardware.Sensor", v14_1);
            if (!v2_2.intercept) {
                v0_8 = v12_0.getDefaultSensor(p26);
                v7_3.postInvoke(v0_8, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12_0, v13_1, v14_1, 1);
            } else {
                v7_3.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12_0, v13_1, v14_1, 0);
                v0_8 = ((android.hardware.Sensor) v2_2.returnValue);
            }
            Boolean v9_1 = this.L;
            if (v9_1 == null) {
                boolean v0_1;
                android.hardware.SensorManager v13_0 = this.LI;
                com.bytedance.helios.statichook.api.HeliosApiHook v8_4 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                Object[] v2_4 = new Object[3];
                v2_4[0] = this;
                v2_4[1] = v0_8;
                v2_4[2] = Integer.valueOf(3);
                com.bytedance.helios.statichook.api.ExtraInfo v4_5 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/hardware/SensorEventListener;Landroid/hardware/Sensor;I)Z", "eSwwXgZ0UITYBw==");
                android.hardware.SensorManager v13_2 = v13_0;
                com.bytedance.helios.statichook.api.Result v7_5 = v8_4.preInvoke(100700, "android/hardware/SensorManager", "registerListener", v13_2, v2_4, "boolean", v4_5);
                if (!v7_5.intercept) {
                    v0_1 = v13_2.registerListener(this, v0_8, 3);
                    v8_4.postInvoke(Boolean.valueOf(v0_1), 100700, "android/hardware/SensorManager", "registerListener", v13_2, v2_4, v4_5, 1);
                } else {
                    v8_4.postInvoke(0, 100700, "android/hardware/SensorManager", "registerListener", v13_2, v2_4, v4_5, 0);
                    v0_1 = ((Boolean) v7_5.returnValue).booleanValue();
                }
                if (!v0_1) {
                    return;
                }
            } else {
                boolean v0_3;
                boolean v5_0 = this.LI;
                int v16_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                Object[] v2_1 = new Object[4];
                v2_1[0] = this;
                v2_1[1] = v0_8;
                v2_1[2] = Integer.valueOf(3);
                v2_1[3] = v9_1;
                com.bytedance.helios.statichook.api.ExtraInfo v4_2 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/hardware/SensorEventListener;Landroid/hardware/Sensor;ILandroid/os/Handler;)Z", "eSwwXgZ0UITYBw==");
                int v16_2 = v16_1;
                com.bytedance.helios.statichook.api.HeliosApiHook v8_1 = v16_2.preInvoke(100700, "android/hardware/SensorManager", "registerListener", v5_0, v2_1, "boolean", v4_2);
                if (!v8_1.intercept) {
                    v0_3 = v5_0.registerListener(this, v0_8, 3, v9_1);
                    v16_2.postInvoke(Boolean.valueOf(v0_3), 100700, "android/hardware/SensorManager", "registerListener", v5_0, v2_1, v4_2, 1);
                } else {
                    v16_2.postInvoke(0, 100700, "android/hardware/SensorManager", "registerListener", v5_0, v2_1, v4_2, 0);
                    v0_3 = ((Boolean) v8_1.returnValue).booleanValue();
                }
                if (!v0_3) {
                    return;
                }
            }
            this.LBL = 1;
            return;
        }
    }

/**
ms.bd.o.d2;LB()V
*/

    public final void LB()
    {
        try {
            int v0_10;
            if ((this.LC.size() % 10) != 0) {
                v0_10 = 0;
            } else {
                v0_10 = 1;
            }
        } catch (int v0_11) {
            throw v0_11;
        }
        if ((v0_10 == 0) || (ms.bd.o.n2.LB() == 1)) {
            this.L(1);
            this.L(9);
            this.L(4);
            this.L(11);
            this.LFI = 1;
            this.L.postDelayed(new ms.bd.o.d2$c(this), this.LCC);
            return;
        } else {
            byte[] v5 = new byte[26];
            v5 = {38, 59, 69, 22, 7, 101, 4, 21, 108, 34, 42, 33, 0, 28, 2, 101, 53, 17, 97, 58, 34, 33, 79, 0, 2, 33};
            ms.bd.o.k.a(16777217, 0, 0, "413a32", v5);
            return;
        }
    }

/**
ms.bd.o.d2;L(I J)V
*/

    public final declared_synchronized void L(int p7, long p8)
    {
        try {
            this.LCC = p8;
            this.LCCII = p7;
            this.LFLL = 0;
            try {
                this.LC.clear();
                this.LICI.LB(this.LC);
            } catch (long v0_0) {
                throw v0_0;
            }
            byte[] v5 = new byte[15];
            v5[0] = 40;
            v5[1] = 35;
            v5[2] = 107;
            v5[3] = 71;
            v5[4] = 7;
            v5[5] = 37;
            v5[6] = 59;
            v5[7] = 28;
            v5[8] = 115;
            v5[9] = 86;
            v5[10] = 45;
            v5[11] = 40;
            v5[12] = 70;
            v5[13] = 71;
            v5[14] = 13;
            long v0_18 = new android.os.HandlerThread(((String) ms.bd.o.k.a(16777217, 0, 0, "480266", v5)));
            this.LFFLLL = v0_18;
            v0_18.start();
            com.bytedance.bpea.transmit.delegate.a v3_3 = new com.bytedance.bpea.transmit.delegate.a(this.LFFLLL.getLooper());
            this.L = v3_3;
            if (!this.LB) {
                this.LB();
                return;
            } else {
                v3_3.postDelayed(new ms.bd.o.d2$b(this), 10000);
                return;
            }
        } catch (long v0_22) {
            throw v0_22;
        }
    }


}