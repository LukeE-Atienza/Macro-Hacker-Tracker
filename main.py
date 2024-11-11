import customtkinter as ctk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Backend Functions
def food_Call(food_query, grams):
    try:
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_query}&search_simple=1&action=process&json=1"
        search_response = requests.get(search_url)
        search_data = search_response.json()

        if search_data['count'] > 0:
            product_code = search_data['products'][0]['code']
            product_url = f"https://world.openfoodfacts.org/api/v0/product/{product_code}.json"
            product_response = requests.get(product_url)
            product_data = product_response.json()

            nutrients = product_data.get('product', {}).get('nutriments', {})
            nutrient_values = {
                "Calories": nutrients.get("energy-kcal_100g", 0),
                "Fats": nutrients.get("fat_100g", 0),
                "Sodium": nutrients.get("sodium_100g", 0),
                "Carbohydrates": nutrients.get("carbohydrates_100g", 0),
                "Protein": nutrients.get("proteins_100g", 0),
            }
            portion_values = {k: (v * grams / 100) for k, v in nutrient_values.items()}
            return portion_values
        else:
            return {"Calories": 0, "Fats": 0, "Sodium": 0, "Carbohydrates": 0, "Protein": 0}
    except Exception as e:
        print(f"Error fetching food data: {e}")
        return {"Calories": 0, "Fats": 0, "Sodium": 0, "Carbohydrates": 0, "Protein": 0}


def calculate_calories_burned(age, height, weight, gender, distance_miles, terrain_difficulty):
    if gender.lower() == 'm':
        calories_per_mile = 0.75 * weight
    else:
        calories_per_mile = 0.65 * weight
    calories_burned = calories_per_mile * distance_miles
    if terrain_difficulty >= 1 and terrain_difficulty <= 4:
        calories_burned *= 1
    elif terrain_difficulty >= 5 and terrain_difficulty <= 7:
        calories_burned *= 1.4
    else:
        calories_burned *= 1.6
    return calories_burned


def BMR(age, height, weight, gender):
    weight = weight / 2.2
    height = height * 2.54
    if gender.lower() == 'm':
        return (10 * weight) + (6.5 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.5 * height) - (5 * age) + 161


# Frontend Class
class NutritionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")  # Set dark mode theme
        ctk.set_default_color_theme("dark-blue")

        self.title("Nutrition Tracker")
        self.geometry("1000x600")
        self.grid_columnconfigure(0, weight=1)  # Left side for inputs
        self.grid_columnconfigure(1, weight=1)  # Right side for output

        self.food_items = []

        # Left Side - Input Fields
        input_frame = ctk.CTkFrame(self, width=400)
        input_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        self.age_entry = self.create_labeled_entry("Age:", input_frame, 0)
        self.height_entry = self.create_labeled_entry("Height (in inches):", input_frame, 1)
        self.weight_entry = self.create_labeled_entry("Weight (in pounds):", input_frame, 2)
        self.gender_entry = self.create_labeled_entry("Gender (M/F):", input_frame, 3)
        self.distance_entry = self.create_labeled_entry("Distance Walked (in miles):", input_frame, 4)
        self.terrain_entry = self.create_labeled_entry("Terrain Difficulty (1-10):", input_frame, 5)

        # Food Input Section
        self.food_entry = self.create_labeled_entry("Food Name:", input_frame, 6)
        self.grams_entry = self.create_labeled_entry("Grams:", input_frame, 7)

        # Food Item Counter
        self.food_counter_label = ctk.CTkLabel(input_frame, text="Food Items Entered: 0", font=("Arial", 14))
        self.food_counter_label.grid(row=8, column=0, columnspan=2, pady=10)

        # Add Food, Calculate, and Exit Buttons
        self.calculate_button = ctk.CTkButton(input_frame, text="Add Food Item", command=self.add_food_item)
        self.calculate_button.grid(row=9, column=0, pady=10, sticky="we")

        self.calculate_totals_button = ctk.CTkButton(input_frame, text="Calculate Totals", command=self.calculate_totals)
        self.calculate_totals_button.grid(row=10, column=0, pady=10, sticky="we")

        self.exit_button = ctk.CTkButton(input_frame, text="Exit", command=self.destroy)
        self.exit_button.grid(row=11, column=0, pady=10, sticky="we")

        # Right Side - Result Display (Output)
        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.grid(row=0, column=1, rowspan=2, sticky="nswe", padx=10, pady=10)

        self.result_text = ctk.CTkTextbox(self.result_frame, height=20, width=40)
        self.result_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Chart Frame for Pie Chart
        self.chart_frame = ctk.CTkFrame(self.result_frame, width=200, height=200)
        self.chart_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Make the output text box resizable
        self.result_text.bind("<Configure>", lambda event: self.result_text.configure(width=event.width, height=event.height))


        # Bind Enter Key for Navigation
        self.bind_navigation()

        # Show Instructions Popup on Start
        self.show_instructions()

    def create_labeled_entry(self, label_text, frame, row):
        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14), anchor="w")  # Left-align the label text
        label.grid(row=row, column=0, pady=5, sticky="w")
        entry = ctk.CTkEntry(frame)
        entry.grid(row=row, column=1, pady=5, sticky="w")
        return entry

    def bind_navigation(self):
        entries = [self.age_entry, self.height_entry, self.weight_entry, self.gender_entry,
                   self.distance_entry, self.terrain_entry, self.food_entry, self.grams_entry]

        for i, entry in enumerate(entries):
            entry.bind("<Return>", lambda e, idx=i: entries[(idx + 1) % len(entries)].focus())

    def show_instructions(self):
        instructions_popup = ctk.CTkToplevel(self)
        instructions_popup.title("Instructions")
        instructions_popup.geometry("400x300")

        instructions_text = (
            "Welcome to the Nutrition Tracker!\n\n"
            "Instructions:\n"
            "- Enter your Age, Height, Weight, and Gender.\n"
            "- Input the Distance Walked and Terrain Difficulty.\n"
            "- Add Food Name and Grams, then click 'Add Food Item' to log items.\n"
            "- Click 'Calculate Totals' to review total nutrition values and chart.\n"
            "- Click 'Exit' to close the application.\n\n"
            "Enjoy tracking your nutrition and calories burned!"
        )

        label = ctk.CTkLabel(instructions_popup, text=instructions_text, font=("Arial", 12), wraplength=380)
        label.pack(pady=20, padx=20)

        understood_button = ctk.CTkButton(instructions_popup, text="Understood", command=instructions_popup.destroy)
        understood_button.pack(pady=10)

    def add_food_item(self):
        food = self.food_entry.get().strip()
        grams = float(self.grams_entry.get().strip())
        if food and grams > 0:
            self.food_items.append((food, grams))
            self.food_counter_label.configure(text=f"Food Items Entered: {len(self.food_items)}")
            self.food_entry.delete(0, ctk.END)
            self.grams_entry.delete(0, ctk.END)

    def calculate_totals(self):
        try:
            # Get Inputs
            age = int(self.age_entry.get())
            height = float(self.height_entry.get())
            weight = float(self.weight_entry.get())
            gender = self.gender_entry.get().strip().lower()
            distance_miles = float(self.distance_entry.get())
            terrain_difficulty = int(self.terrain_entry.get())

            total_nutrients = {"Calories": 0, "Fats": 0, "Sodium": 0, "Carbohydrates": 0, "Protein": 0}
            result_text = "Individual Food Items:\n\n"
            for food, grams in self.food_items:
                nutrients = food_Call(food, grams)
                result_text += (
                    f"{food} ({grams}g):\n"
                    f"  Calories: {nutrients['Calories']:.2f} kcal\n"
                    f"  Fats: {nutrients['Fats']:.2f} g\n"
                    f"  Sodium: {nutrients['Sodium']:.2f} g\n"
                    f"  Carbohydrates: {nutrients['Carbohydrates']:.2f} g\n"
                    f"  Protein: {nutrients['Protein']:.2f} g\n\n"
                )
                for key in total_nutrients:
                    total_nutrients[key] += nutrients.get(key, 0)

            calories_burned = calculate_calories_burned(age, height, weight, gender, distance_miles, terrain_difficulty)
            bmr = BMR(age, height, weight, gender)
            delta_calories = total_nutrients["Calories"] - calories_burned

            # Display Results
            result_text += (
                "Total Nutritional Info:\n"
                f"  Calories: {total_nutrients['Calories']:.2f} kcal\n"
                f"  Fats: {total_nutrients['Fats']:.2f} g\n"
                f"  Sodium: {total_nutrients['Sodium']:.2f} g\n"
                f"  Carbohydrates: {total_nutrients['Carbohydrates']:.2f} g\n"
                f"  Protein: {total_nutrients['Protein']:.2f} g\n\n"
                f"Calories Burned: {calories_burned:.2f} kcal\n"
                f"BMR: {bmr:.2f} kcal\n"
                f"Delta Calories (Food - Burned): {delta_calories:.2f} kcal\n\n"
            )

            # Analysis of Nutrition and Activity
            if delta_calories > 0:
                analysis_text = (
                    "You have consumed more calories than you burned, "
                    "which may result in a caloric surplus. This is ideal for gaining weight "
                    "or muscle, assuming balanced macronutrient intake. Consider balancing "
                    "with additional activity if you aim for a caloric deficit.\n"
                )
            elif delta_calories < 0:
                analysis_text = (
                    "You are in a caloric deficit, which may lead to weight loss. "
                    "If this is your goal, ensure protein intake remains sufficient "
                    "to preserve muscle mass.\n"
                )
            else:
                analysis_text = (
                    "Your caloric intake matches your calories burned, promoting weight "
                    "maintenance. For muscle growth or other fitness goals, you might adjust "
                    "macronutrient intake.\n"
                )

            result_text += analysis_text

            self.result_text.delete("1.0", ctk.END)
            self.result_text.insert(ctk.END, result_text)

            # Plot Pie Chart
            self.plot_pie_chart(total_nutrients)

        except Exception as e:
            self.result_text.delete("1.0", ctk.END)
            self.result_text.insert(ctk.END, f"Error: {str(e)}\n")


    def plot_pie_chart(self, nutrients):
        # Nutrients to plot
        labels = ['Fats (g)', 'Carbohydrates (g)', 'Protein (g)']
        sizes = [nutrients['Fats'], nutrients['Carbohydrates'], nutrients['Protein']]
        colors = ['#ff9999','#66b3ff','#99ff99']
        explode = (0.1, 0, 0)  # Explode the 1st slice (Fats)

        fig, ax = plt.subplots()
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Clear previous canvas if any
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Embed the plot into the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

if __name__ == "__main__":
    app = NutritionApp()
    app.mainloop()