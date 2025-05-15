from control_drone import control_drone



def detect_obj(cv2, model, cap, drone):
    window_name = "Object Detection"

    # Проверяем, открылась ли камера
    if not cap.isOpened():
        print("Ошибка: Не удалось открыть камеру")
        exit()

    # Переменные для трекинга
    target_object_id = None  # ID объекта, который будем отслеживать
    target_object = None  # Информация о целевом объекте
    try:
        while True:
            # Читаем кадр
            ret, frame = cap.read()
            if not ret:
                print("Ошибка: Не удалось захватить кадр")
                break

            # Получаем размеры кадра
            height, width = frame.shape[:2]
            frame_area = width * height  # Площадь кадра в пикселях

            # Выполняем детекцию и трекинг объектов
            results = model.track(frame, persist=True, tracker="botsort.yaml")

            # Если объект ещё не зафиксирован, ищем самый большой
            if target_object_id is None:
                max_area_percent = 0
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        if box.id is None:  # Пропускаем, если ID не присвоен
                            continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf)
                        class_id = int(box.cls)
                        class_name = "Object"  # Можно заменить на model.names[class_id]
                        object_area = (x2 - x1) * (y2 - y1)
                        area_percent = (object_area / frame_area) * 100

                        # Ищем объект с наибольшей площадью
                        if area_percent > max_area_percent:
                            max_area_percent = area_percent
                            target_object_id = int(box.id)  # Фиксируем ID объекта
                            target_object = {
                                "box": (x1, y1, x2, y2),
                                "class_name": class_name,
                                "confidence": confidence,
                                "area_percent": area_percent
                            }

            # Если объект зафиксирован, ищем его по ID
            else:
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        if box.id is None:
                            continue

                        if int(box.id) == target_object_id:  # Нашли наш объект
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            confidence = float(box.conf)
                            class_id = int(box.cls)
                            class_name = "Object"  # Можно заменить на model.names[class_id]
                            object_area = (x2 - x1) * (y2 - y1)
                            area_percent = (object_area / frame_area) * 100

                            target_object = {
                                "box": (x1, y1, x2, y2),
                                "class_name": class_name,
                                "confidence": confidence,
                                "area_percent": area_percent
                            }
                            break
                    else:
                        # Если объект с target_object_id не найден в кадре, сбрасываем фиксацию
                        target_object = None
                        target_object_id = None

            # Если есть целевой объект, рисуем его
            if target_object:
                x1, y1, x2, y2 = target_object["box"]
                class_name = target_object["class_name"]
                confidence = target_object["confidence"]
                area_percent = target_object["area_percent"]

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                print(f"Target Object ID: {target_object_id}, Coordinates: (x1={x1}, y1={y1}, x2={x2}, y2={y2})")
                control_drone(center_x, center_y, target_object_id, confidence, area_percent, drone)

                # Рисуем bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Добавляем текст с информацией
                label = f"{class_name} ({confidence:.2f}) | {area_percent:.1f}% | ID: {target_object_id}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Отображаем кадр
            cv2.imshow("Object Detection", frame)

            # Выход по нажатию клавиши 'q'
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("Программа завершена: окно закрыто")
                break

    except KeyboardInterrupt:
        print("Программа завершена пользователем (Ctrl+C)")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()