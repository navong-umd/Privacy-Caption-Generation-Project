/*Application Package Name: com.tiktok.lite.go
class PRCS_407 {
/**
X.4KW;L()Z
*/

    public static boolean L()
    {
        android.location.LocationManager v2_1 = ((android.location.LocationManager) X.4KW.L.getValue());
        if (v2_1 == null) {
            return 0;
        } else {
            if ((v2_1.isProviderEnabled("gps")) || (v2_1.isProviderEnabled("network"))) {
                return 1;
            } else {
                return 0;
            }
        }
    }

/**
X.4RS;L()V
*/

    public final void L()
    {
        String v4_2 = ((String) this.LBL.get(this.L));
        X.5PY v0_2 = new X.5PY(this, v4_2, 6);
        android.app.Activity v11 = X.16G.LI.L();
        int v1_2 = Boolean.valueOf(0);
        if (v11 != null) {
            android.content.Intent v3_2 = v4_2.hashCode();
            if (v3_2 == 3649301) {
                if (v4_2.equals("wifi")) {
                    if ((v11.isDestroyed()) || (v11.isFinishing())) {
                        v0_2.invoke(v1_2);
                        return;
                    } else {
                        android.content.Intent v3_3 = new String[] {"android.permission.ACCESS_WIFI_STATE", "android.permission.CHANGE_WIFI_STATE"});
                        if (android.os.Build$VERSION.SDK_INT >= 29) {
                            X.5Pc v2_21 = X.5ue.L(v11, v3_3);
                            if (!((java.util.Collection) v2_21).isEmpty()) {
                                X.5Pc v2_22 = v2_21.iterator();
                                while (v2_22.hasNext()) {
                                    if (!((Boolean) v2_22.next()).booleanValue()) {
                                        X.5ue.L(v11, v3_3, new X.5Pc(v11, v0_2, 17));
                                        return;
                                    }
                                }
                            }
                        }
                        X.4Kc.L(v11, v0_2);
                        return;
                    }
                }
            } else {
                if (v3_2 == 1901043637) {
                    if (v4_2.equals("location")) {
                        if (!X.4KW.L()) {
                            if ((v11.isDestroyed()) || (v11.isFinishing())) {
                                v0_2.invoke(v1_2);
                                return;
                            } else {
                                android.content.Intent v3_4 = v11.getApplication();
                                v3_4.registerActivityLifecycleCallbacks(new X.4KV(v3_4, v0_2));
                                try {
                                    android.content.Intent v3_6 = new android.content.Intent("android.settings.LOCATION_SOURCE_SETTINGS");
                                    com.bytedance.helios.statichook.api.HeliosApiHook v6_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                                    Object[] v12 = new Object[2];
                                    v12[0] = v3_6;
                                    v12[1] = Integer.valueOf(1);
                                    com.bytedance.helios.statichook.api.ExtraInfo v13_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/content/Intent;I)V", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPmtd4vH0jV92xn0HeLRch6i+1BX728nqA==");
                                } catch (Exception) {
                                    v0_2.invoke(v1_2);
                                    return;
                                }
                                if (!v6_1.preInvoke(11094, "android/app/Activity", "startActivityForResult", v11, v12, "void", v13_1).intercept) {
                                    v11.startActivityForResult(v3_6, 1);
                                    v6_1.postInvoke(0, 11094, "android/app/Activity", "startActivityForResult", v11, v12, v13_1, 1);
                                    return;
                                } else {
                                    v6_1.postInvoke(0, 11094, "android/app/Activity", "startActivityForResult", v11, v12, v13_1, 0);
                                    return;
                                }
                            }
                        } else {
                            v0_2.invoke(Boolean.valueOf(1));
                            return;
                        }
                    }
                } else {
                    if ((v3_2 == 1968882350) && (v4_2.equals("bluetooth"))) {
                        if ((v11.isDestroyed()) || (v11.isFinishing())) {
                            v0_2.invoke(v1_2);
                            return;
                        } else {
                            android.content.Intent v3_1 = new String[] {"android.permission.BLUETOOTH_ADMIN", "android.permission.BLUETOOTH_CONNECT", "android.permission.BLUETOOTH_SCAN", "android.permission.BLUETOOTH_ADVERTISE"});
                            if (android.os.Build$VERSION.SDK_INT >= 31) {
                                X.5Pc v2_10 = X.5ue.L(v11, v3_1);
                                if (!((java.util.Collection) v2_10).isEmpty()) {
                                    X.5Pc v2_11 = v2_10.iterator();
                                    while (v2_11.hasNext()) {
                                        if (!((Boolean) v2_11.next()).booleanValue()) {
                                            X.5ue.L(v11, v3_1, new X.5Pc(v11, v0_2, 16));
                                            return;
                                        }
                                    }
                                }
                            }
                            X.4KU.L(v11, v0_2);
                            return;
                        }
                    }
                }
            }
            v0_2.invoke(v1_2);
            return;
        } else {
            v0_2.invoke(v1_2);
            return;
        }
    }

/**
X.5PY;invoke$6(LX/5PY; Ljava/lang/Object;)Ljava/lang/Object;
*/

    public static final synthetic Object invoke$6(X.5PY p4, Object p5)
    {
        ((X.4RS) p4.l1).LB.put(p4.s0, Integer.valueOf(((Boolean) p5).booleanValue()));
        kotlin.jvm.functions.Function1 v1_1 = ((X.4RS) p4.l1);
        v1_1.L = (v1_1.L + 1);
        if (v1_1.L >= ((X.4RS) p4.l1).LBL.size()) {
            ((X.4RS) p4.l1).LC.invoke(((X.4RS) p4.l1).LB);
        } else {
            ((X.4RS) p4.l1).L();
        }
        return kotlin.Unit.L;
    }


}